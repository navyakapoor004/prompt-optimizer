import json
import os
import re
import urllib.request
import urllib.error
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import PromptHistory


SYSTEM_OPTIMIZER_PROMPT = """You are an expert Prompt Engineer. Your job is to transform raw, vague user queries into highly optimized prompts for AI systems like ChatGPT.

When optimizing a prompt, always:
1. Add a clear ROLE (e.g., "Act as an expert software engineer...")
2. Add CONTEXT about what the user needs
3. Specify the desired OUTPUT FORMAT (step-by-step, bullet points, table, etc.)
4. Add CONSTRAINTS or requirements
5. Make it SPECIFIC and DETAILED

Respond ONLY with a JSON object in this exact format:
{
  "optimized_prompt": "The fully optimized prompt here",
  "category": "The category of this prompt (e.g., Coding, Education, Creative, Business, etc.)",
  "improvements": ["improvement 1", "improvement 2", "improvement 3"],
  "explanation": "Brief explanation of what was improved"
}"""


def call_openai_api(messages, system_prompt=None, api_key=None):
    """Call OpenAI API using urllib (no external dependencies)"""
    if not api_key:
        api_key = os.environ.get('OPENAI_API_KEY', '')
    
    if not api_key:
        return None, "API key not configured"

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [],
        "temperature": 0.7,
        "max_tokens": 1500
    }

    if system_prompt:
        payload["messages"].append({"role": "system", "content": system_prompt})
    
    payload["messages"].extend(messages)

    data = json.dumps(payload).encode('utf-8')
    
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result['choices'][0]['message']['content'], None
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        try:
            error_data = json.loads(error_body)
            return None, error_data.get('error', {}).get('message', str(e))
        except:
            return None, str(e)
    except Exception as e:
        return None, str(e)


def optimize_prompt_locally(raw_prompt):
    """Fallback: optimize prompt without API using rule-based approach"""
    prompt_lower = raw_prompt.lower()
    
    # Detect category
    if any(w in prompt_lower for w in ['code', 'program', 'function', 'bug', 'python', 'javascript', 'django', 'api']):
        category = "Coding & Development"
        role = "Act as an expert software engineer and programming mentor"
        format_hint = "Provide a step-by-step solution with code examples, explanations for each step, and best practices."
    elif any(w in prompt_lower for w in ['explain', 'teach', 'learn', 'understand', 'what is', 'how does']):
        category = "Education & Learning"
        role = "Act as an experienced teacher and subject matter expert"
        format_hint = "Explain in simple terms with examples, analogies, and a summary at the end."
    elif any(w in prompt_lower for w in ['write', 'essay', 'story', 'content', 'blog', 'article']):
        category = "Creative Writing"
        role = "Act as a professional writer and content creator"
        format_hint = "Structure the content with a clear introduction, body, and conclusion. Use engaging language."
    elif any(w in prompt_lower for w in ['business', 'marketing', 'strategy', 'plan', 'startup']):
        category = "Business & Strategy"
        role = "Act as a seasoned business consultant and strategist"
        format_hint = "Provide actionable insights in a structured format with key points, pros/cons, and recommendations."
    else:
        category = "General"
        role = "Act as a knowledgeable expert in the relevant domain"
        format_hint = "Provide a comprehensive, well-structured response with clear sections."

    optimized = f"""{role} with years of experience.

Task: {raw_prompt}

Requirements:
- Provide a detailed and accurate response
- {format_hint}
- Include relevant examples where appropriate
- Highlight any important considerations or caveats
- End with a brief summary or key takeaways

Please ensure your response is thorough, practical, and easy to understand."""

    improvements = [
        f"Added expert role: '{role}'",
        "Specified output format and structure",
        "Added requirements for examples and clarity",
        "Requested summary/key takeaways"
    ]

    return {
        "optimized_prompt": optimized,
        "category": category,
        "improvements": improvements,
        "explanation": "Enhanced with role assignment, format specification, and clarity requirements using rule-based optimization."
    }


def index(request):
    recent_history = PromptHistory.objects.all()[:10]
    return render(request, 'optimizer/index.html', {'recent_history': recent_history})


def history_view(request):
    all_history = PromptHistory.objects.all()
    return render(request, 'optimizer/history.html', {'history': all_history})


def history_detail(request, pk):
    item = get_object_or_404(PromptHistory, pk=pk)
    return render(request, 'optimizer/history_detail.html', {'item': item})


@csrf_exempt
@require_http_methods(["POST"])
def optimize_prompt(request):
    try:
        data = json.loads(request.body)
        raw_prompt = data.get('prompt', '').strip()
        api_key = data.get('api_key', '').strip()

        if not raw_prompt:
            return JsonResponse({'error': 'Prompt cannot be empty'}, status=400)

        # Try OpenAI API first
        response_text, error = call_openai_api(
            [{"role": "user", "content": f"Optimize this prompt: {raw_prompt}"}],
            system_prompt=SYSTEM_OPTIMIZER_PROMPT,
            api_key=api_key
        )

        if response_text:
            try:
                # Clean up response
                cleaned = response_text.strip()
                if cleaned.startswith('```'):
                    cleaned = re.sub(r'^```(?:json)?\n?', '', cleaned)
                    cleaned = re.sub(r'\n?```$', '', cleaned)
                result = json.loads(cleaned)
                result['source'] = 'openai'
            except json.JSONDecodeError:
                result = optimize_prompt_locally(raw_prompt)
                result['source'] = 'local'
        else:
            result = optimize_prompt_locally(raw_prompt)
            result['source'] = 'local'
            if error:
                result['api_note'] = f"Using local optimization. API error: {error}"

        # Save to history
        history_item = PromptHistory.objects.create(
            raw_prompt=raw_prompt,
            optimized_prompt=result['optimized_prompt'],
            category=result.get('category', 'General')
        )
        result['history_id'] = history_item.pk

        return JsonResponse(result)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def get_ai_response(request):
    try:
        data = json.loads(request.body)
        optimized_prompt = data.get('optimized_prompt', '').strip()
        history_id = data.get('history_id')
        api_key = data.get('api_key', '').strip()

        if not optimized_prompt:
            return JsonResponse({'error': 'Optimized prompt cannot be empty'}, status=400)

        response_text, error = call_openai_api(
            [{"role": "user", "content": optimized_prompt}],
            api_key=api_key
        )

        if error:
            return JsonResponse({'error': error}, status=400)

        if history_id:
            try:
                item = PromptHistory.objects.get(pk=history_id)
                item.ai_response = response_text
                item.save()
            except PromptHistory.DoesNotExist:
                pass

        return JsonResponse({'response': response_text})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_history(request, pk):
    item = get_object_or_404(PromptHistory, pk=pk)
    item.delete()
    return JsonResponse({'success': True})
