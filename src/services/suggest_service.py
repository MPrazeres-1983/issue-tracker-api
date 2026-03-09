"""Issue classification suggestion service using LLM."""

import json
import os
from typing import Optional
from src.utils.logger import logger


SYSTEM_PROMPT = (
    "You are a precise software issue classifier. "
    "Analyse the issue title and description and return ONLY valid JSON. "
    "No explanations, no markdown, no code blocks."
)

CLASSIFY_TEMPLATE = """Classify the following software issue.

Priority definitions:
- "critical": system down, data loss, security breach, complete feature failure blocking all users
- "high": important feature broken with no workaround, significant performance degradation
- "medium": feature partially broken, workaround exists, moderate impact
- "low": cosmetic issues, minor inconveniences, feature requests, suggestions

Status definitions:
- "open": new issue, not yet triaged
- "in_progress": actively being worked on
- "resolved": fix implemented, pending verification
- "closed": verified fixed or rejected

Issue title: {title}
Issue description: {description}

Respond ONLY with a JSON object with these exact fields:
- priority: string (critical | high | medium | low)
- status: string (open | in_progress | resolved | closed)
- confidence: string (high | medium | low)
- reason: string (one sentence explaining the classification)"""


class SuggestService:
    """Service for AI-powered issue classification suggestions."""

    def suggest(
        self,
        title: str,
        description: Optional[str] = None,
    ) -> tuple[dict, Optional[str]]:
        """
        Suggest priority and status for an issue using LLM.

        Args:
            title: Issue title
            description: Issue description (optional)

        Returns:
            Tuple of (suggestion_dict, error_message)
        """
        try:
            from openai import OpenAI

            api_key = os.getenv("OPENAI_API_KEY")
            base_url = os.getenv("OPENAI_BASE_URL")
            model = os.getenv("SUGGEST_MODEL", "llama-3.3-70b-versatile")

            if not api_key:
                return {}, "OPENAI_API_KEY not configured"

            client = OpenAI(api_key=api_key, base_url=base_url or None)

            prompt = CLASSIFY_TEMPLATE.format(
                title=title,
                description=description or "(no description provided)",
            )

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
                max_tokens=256,
            )

            raw = response.choices[0].message.content or "{}"

            # Strip markdown code blocks if model adds them
            clean = raw.strip()
            if clean.startswith("```"):
                clean = "\n".join(clean.split("\n")[1:])
            if clean.endswith("```"):
                clean = "\n".join(clean.split("\n")[:-1])

            suggestion = json.loads(clean.strip())

            # Validate required fields
            valid_priorities = {"critical", "high", "medium", "low"}
            valid_statuses = {"open", "in_progress", "resolved", "closed"}

            if suggestion.get("priority") not in valid_priorities:
                suggestion["priority"] = "medium"
            if suggestion.get("status") not in valid_statuses:
                suggestion["status"] = "open"
            if "confidence" not in suggestion:
                suggestion["confidence"] = "medium"
            if "reason" not in suggestion:
                suggestion["reason"] = ""

            logger.info(f"Issue classified: priority={suggestion['priority']} confidence={suggestion['confidence']}")
            return suggestion, None

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return {}, "Failed to parse classification response"
        except Exception as e:
            logger.error(f"Suggest service error: {e}")
            return {}, f"Classification failed: {str(e)}"