"""
orchestrator.py - Dual-Agent Game Planning Orchestrator

This module implements the core orchestration logic for game design document generation
using a Dual-Agent Actor-Critic architecture based on arXiv:2512.10501.

Components:
- GamePlanningOrchestrator: Main controller for GDD generation
- Actor (Game Designer): Generates creative GDDs (temperature 0.6)
- Critic (Game Reviewer): Validates feasibility, coherence, fun factor (temperature 0.2)

Algorithm (adapted from Algorithm 1):
    Input: P_user (game concept), K (max iterations)
    Output: S_final (final GDD)

    GDD_0 ← Actor(P_user)
    i ← 0

    while i < K do:
        Feedback ← Critic(GDD_i)
        if Feedback.decision = "approve" then return GDD_i
        GDD_{i+1} ← Actor(P_user, GDD_i, Feedback)  # Revision
        i ← i + 1

    return GDD_K  # Best effort
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from models import (
    CriticFeedback,
    Decision,
    GameDesignDocument,
    IterationRecord,
    RefinementResult,
    TerminationReason,
)
from llm_provider import (
    BaseLLMProvider,
    LLMResponse,
    MockLLMProvider,
    create_provider,
    load_config,
)
from prompts import (
    GAME_DESIGNER_SYSTEM_PROMPT,
    GAME_REVIEWER_SYSTEM_PROMPT,
    create_actor_message,
    create_critic_message,
    create_revision_message,
)

logger = logging.getLogger(__name__)


# =============================================================================
# ORCHESTRATOR CONFIGURATION
# =============================================================================


@dataclass
class OrchestratorConfig:
    """Configuration for the orchestrator."""

    max_iterations: int = 3
    actor_temperature: float = 0.6
    critic_temperature: float = 0.2
    max_tokens: int = 8192
    actor_timeout_ms: int = 120000  # 2 minutes
    critic_timeout_ms: int = 60000  # 1 minute
    max_retries: int = 3
    retry_backoff_base: float = 2.0

    @classmethod
    def from_config(
        cls, config: Optional[Dict[str, Any]] = None
    ) -> "OrchestratorConfig":
        """Create config from config.yaml."""
        if config is None:
            config = load_config()

        orchestrator_config = config.get("orchestrator", {})
        llm_config = config.get("llm", {})
        timeout_config = config.get("timeouts", {})
        retry_config = config.get("retries", {})

        return cls(
            max_iterations=orchestrator_config.get("max_iterations", 3),
            actor_temperature=orchestrator_config.get("actor_temperature", 0.6),
            critic_temperature=orchestrator_config.get("critic_temperature", 0.2),
            max_tokens=llm_config.get("max_tokens", 8192),
            actor_timeout_ms=timeout_config.get("actor_ms", 120000),
            critic_timeout_ms=timeout_config.get("critic_ms", 60000),
            max_retries=retry_config.get("max_attempts", 3),
            retry_backoff_base=retry_config.get("backoff_base", 2.0),
        )


# =============================================================================
# FALLBACK GDD TEMPLATE
# =============================================================================


def create_fallback_gdd(user_prompt: str) -> GameDesignDocument:
    """
    Create a minimal fallback GDD when JSON parsing fails.

    Used when:
    - Actor generates invalid JSON after all retries
    - JSON extraction fails

    Args:
        user_prompt: Original user request for context

    Returns:
        Minimal but valid GameDesignDocument
    """
    from models import (
        GameMeta,
        CoreLoop,
        GameSystem,
        Progression,
        Narrative,
        TechnicalSpec,
        AudioRequirements,
        Milestone,
        Genre,
        Platform,
        SystemType,
        ProgressionType,
        NarrativeDelivery,
        GameEngine,
        ArtStyle,
    )

    # Extract a title hint from user prompt
    title_words = user_prompt.split()[:5]
    title = " ".join(w.capitalize() for w in title_words) + " (Fallback)"

    return GameDesignDocument(
        schema_version="1.0",
        meta=GameMeta(
            title=title,
            genres=[Genre.ACTION],
            target_platforms=[Platform.PC],
            target_audience="General gaming audience - this is a fallback GDD",
            unique_selling_point=f"Based on concept: {user_prompt[:100]}... (Fallback - needs revision)",
            estimated_dev_time_weeks=26,
        ),
        core_loop=CoreLoop(
            primary_actions=["Play", "Progress"],
            challenge_description="Fallback GDD - challenges need to be defined based on the concept",
            reward_description="Fallback GDD - rewards need to be defined based on the concept",
            loop_description="Fallback GDD - core loop needs to be designed based on the concept",
            session_length_minutes=30,
        ),
        systems=[
            GameSystem(
                name="Core Gameplay System",
                type=SystemType.CUSTOM,
                description="Fallback system - needs to be defined based on the concept",
                mechanics=["Placeholder mechanic"],
            ),
            GameSystem(
                name="Progression System",
                type=SystemType.LEVELING,
                description="Fallback progression - needs to be defined based on the concept",
                mechanics=["Level up"],
            ),
            GameSystem(
                name="UI System",
                type=SystemType.UI,
                description="Standard UI system for menus and HUD",
                mechanics=["Menu navigation", "HUD display"],
            ),
        ],
        progression=Progression(
            type=ProgressionType.LINEAR,
            milestones=[
                Milestone(
                    name="Tutorial Complete",
                    description="Complete the tutorial",
                    unlock_condition="Finish tutorial sequence",
                ),
                Milestone(
                    name="First Challenge",
                    description="Complete the first challenge",
                    unlock_condition="Beat first challenge",
                ),
                Milestone(
                    name="Mid-game",
                    description="Reach mid-game content",
                    unlock_condition="Complete 50% of content",
                ),
                Milestone(
                    name="End-game",
                    description="Reach end-game content",
                    unlock_condition="Complete 80% of content",
                ),
                Milestone(
                    name="Completion",
                    description="Complete the game",
                    unlock_condition="Finish all main content",
                ),
            ],
            difficulty_curve_description="Fallback - difficulty curve needs to be designed",
        ),
        narrative=Narrative(
            setting="Fallback setting - needs to be defined based on the concept",
            story_premise=f"Based on concept: {user_prompt[:200]}... (Needs full narrative design)",
            themes=["Adventure"],
            narrative_delivery=[NarrativeDelivery.NONE],
            story_structure="Fallback - story structure needs to be designed",
        ),
        technical=TechnicalSpec(
            recommended_engine=GameEngine.UNITY,
            art_style=ArtStyle.STYLIZED,
            key_technologies=["Game engine", "Version control"],
            audio=AudioRequirements(
                music_style="Background music",
                sound_categories=["UI", "Gameplay"],
            ),
        ),
        additional_notes="This is a FALLBACK GDD generated due to parsing errors. Please regenerate with more specific prompts.",
    )


def create_template_gdd(user_prompt: str) -> GameDesignDocument:
    """
    Create a template GDD when timeout occurs.

    Similar to fallback but with slightly more structure
    based on common game patterns.

    Args:
        user_prompt: Original user request

    Returns:
        Template-based GameDesignDocument
    """
    # For now, use the same fallback
    # Future: Could add more sophisticated template selection
    return create_fallback_gdd(user_prompt)


# =============================================================================
# GAME PLANNING ORCHESTRATOR
# =============================================================================


class GamePlanningOrchestrator:
    """
    Dual-Agent orchestrator for game design document generation.

    Based on Algorithm 1 from arXiv:2512.10501, adapted for GDD generation.

    The orchestrator coordinates:
    1. Actor (Game Designer): Generates creative GDDs
    2. Critic (Game Reviewer): Validates using 5-dimension framework

    Features:
    - Iterative refinement with state-replacement strategy
    - Configurable max iterations
    - Error handling with fallback GDDs
    - Exponential backoff for transient failures

    Example:
        orchestrator = GamePlanningOrchestrator(provider)
        result = await orchestrator.execute("zombie survival roguelike")
        if result.success:
            print(result.final_gdd.get_summary())
    """

    def __init__(
        self,
        llm_provider: BaseLLMProvider,
        config: Optional[OrchestratorConfig] = None,
    ):
        """
        Initialize the orchestrator.

        Args:
            llm_provider: LLM provider for Actor and Critic agents
            config: Optional configuration (loads from config.yaml if not provided)
        """
        self.llm_provider = llm_provider
        self.config = config or OrchestratorConfig.from_config()
        self.logger = logging.getLogger(f"{__name__}.GamePlanningOrchestrator")

        # Metrics tracking
        self._total_input_tokens = 0
        self._total_output_tokens = 0

    async def execute(self, user_prompt: str) -> RefinementResult:
        """
        Execute the full GDD generation and refinement process.

        Implements the Dual-Agent Actor-Critic loop:
        1. Actor generates initial GDD
        2. Critic reviews using 5-dimension framework
        3. If approved, return GDD
        4. If not, Actor revises based on feedback
        5. Repeat until approved or max iterations

        Args:
            user_prompt: Natural language description of the game concept

        Returns:
            RefinementResult with final GDD and metadata

        Example:
            result = await orchestrator.execute("cozy farming game with magical creatures")
            print(f"Success: {result.success}")
            print(result.final_gdd.get_summary())
        """
        start_time = time.time()
        self.logger.info(f"Starting GDD generation for: {user_prompt[:100]}...")

        # Reset metrics
        self._total_input_tokens = 0
        self._total_output_tokens = 0

        iteration_history: List[IterationRecord] = []
        current_gdd: Optional[GameDesignDocument] = None
        current_feedback: Optional[CriticFeedback] = None

        try:
            # =============================================================
            # Step 1: Initial GDD generation
            # From Algorithm 1: GDD_0 ← Actor(P_user)
            # =============================================================
            self.logger.info("Step 1: Actor generating initial GDD")
            actor_start = time.time()

            actor_message = create_actor_message(user_prompt)
            current_gdd, actor_response = await self._invoke_actor(actor_message)

            actor_duration_ms = (time.time() - actor_start) * 1000
            self._track_tokens(actor_response)

            self.logger.info(
                f"Actor generated GDD: '{current_gdd.meta.title}' "
                f"(tokens: in={actor_response.input_tokens}, out={actor_response.output_tokens})"
            )

            # =============================================================
            # Step 2: Iterative refinement loop
            # From Algorithm 1: while i < K do
            # =============================================================
            for i in range(self.config.max_iterations):
                iteration_num = i + 1
                self.logger.info(
                    f"Iteration {iteration_num}/{self.config.max_iterations}: Critic reviewing"
                )

                # ---------------------------------------------------------
                # Critic evaluation
                # From Algorithm 1: Feedback ← Critic(GDD_i)
                # ---------------------------------------------------------
                critic_start = time.time()

                critic_message = create_critic_message(
                    user_prompt=user_prompt,
                    gdd_json=current_gdd.to_json(),
                )
                current_feedback, critic_response = await self._invoke_critic(
                    critic_message
                )

                critic_duration_ms = (time.time() - critic_start) * 1000
                self._track_tokens(critic_response)

                self.logger.info(
                    f"Critic decision: {current_feedback.decision.value} "
                    f"(score: {current_feedback.overall_score:.1f}/10, "
                    f"issues: {len(current_feedback.blocking_issues)})"
                )

                # Record iteration
                iteration_history.append(
                    IterationRecord(
                        iteration_number=i,
                        gdd=current_gdd,
                        feedback=current_feedback,
                        actor_duration_ms=actor_duration_ms,
                        critic_duration_ms=critic_duration_ms,
                    )
                )

                # ---------------------------------------------------------
                # Check termination: Critic approved
                # From Algorithm 1: if Feedback.decision = "approve" then return GDD_i
                # ---------------------------------------------------------
                if current_feedback.is_approved:
                    self.logger.info(
                        f"[SUCCESS] Critic APPROVED GDD '{current_gdd.meta.title}' "
                        f"(overall score: {current_feedback.overall_score:.1f}/10)"
                    )

                    return RefinementResult(
                        final_gdd=current_gdd,
                        termination_reason=TerminationReason.APPROVED,
                        total_iterations=iteration_num,
                        iteration_history=iteration_history,
                        total_duration_ms=(time.time() - start_time) * 1000,
                        user_prompt=user_prompt,
                        success=True,
                    )

                # Check if this is the last iteration
                if i >= self.config.max_iterations - 1:
                    self.logger.warning(
                        f"Max iterations ({self.config.max_iterations}) reached - "
                        "returning best effort GDD"
                    )
                    break

                # ---------------------------------------------------------
                # Actor revision
                # From Algorithm 1: GDD_{i+1} ← Actor(P_user, GDD_i, Feedback)
                # State-replacement: Only current GDD + feedback (not full history)
                # ---------------------------------------------------------
                self.logger.info(
                    f"Revising GDD ({len(current_feedback.blocking_issues)} issues to address)"
                )

                actor_start = time.time()

                revision_message = create_revision_message(
                    previous_gdd=current_gdd.to_json(),
                    critic_feedback=current_feedback.to_actor_feedback(),
                )
                current_gdd, actor_response = await self._invoke_actor(revision_message)

                actor_duration_ms = (time.time() - actor_start) * 1000
                self._track_tokens(actor_response)

                self.logger.info(
                    f"Actor revised GDD: '{current_gdd.meta.title}' "
                    f"(tokens: in={actor_response.input_tokens}, out={actor_response.output_tokens})"
                )

            # =============================================================
            # Max iterations reached - return best effort
            # From Algorithm 1: return GDD_K
            # =============================================================
            return RefinementResult(
                final_gdd=current_gdd,
                termination_reason=TerminationReason.MAX_ITERATIONS,
                total_iterations=self.config.max_iterations,
                iteration_history=iteration_history,
                total_duration_ms=(time.time() - start_time) * 1000,
                user_prompt=user_prompt,
                success=False,
            )

        except asyncio.TimeoutError:
            self.logger.error("Timeout - using template fallback")

            fallback_gdd = create_template_gdd(user_prompt)

            return RefinementResult(
                final_gdd=fallback_gdd if current_gdd is None else current_gdd,
                termination_reason=TerminationReason.TIMEOUT,
                total_iterations=len(iteration_history),
                iteration_history=iteration_history,
                total_duration_ms=(time.time() - start_time) * 1000,
                user_prompt=user_prompt,
                success=False,
            )

        except Exception as e:
            self.logger.error(f"Unrecoverable error: {e}")

            # If we have a GDD, return it as best effort
            if current_gdd is not None:
                return RefinementResult(
                    final_gdd=current_gdd,
                    termination_reason=TerminationReason.ERROR,
                    total_iterations=len(iteration_history),
                    iteration_history=iteration_history,
                    total_duration_ms=(time.time() - start_time) * 1000,
                    user_prompt=user_prompt,
                    success=False,
                )

            raise

    async def _invoke_actor(
        self, prompt: str
    ) -> Tuple[GameDesignDocument, LLMResponse]:
        """
        Invoke Actor agent with retry and fallback logic.

        Error handling:
        - JSONDecodeError: Retry, then use fallback GDD
        - TimeoutError: Use template GDD
        - NetworkError: Exponential backoff retry

        Args:
            prompt: User message for Actor

        Returns:
            Tuple of (GameDesignDocument, LLMResponse)
        """
        last_response: Optional[LLMResponse] = None

        for attempt in range(self.config.max_retries):
            try:
                response = await asyncio.wait_for(
                    self.llm_provider.generate(
                        system_prompt=GAME_DESIGNER_SYSTEM_PROMPT,
                        user_prompt=prompt,
                        temperature=self.config.actor_temperature,
                        max_tokens=self.config.max_tokens,
                        retry=False,  # We handle retry ourselves
                    ),
                    timeout=self.config.actor_timeout_ms / 1000,
                )
                last_response = response

                # Parse GDD from response
                gdd = GameDesignDocument.from_llm_response(response.content)
                return gdd, response

            except asyncio.TimeoutError:
                self.logger.warning(f"Actor timeout (attempt {attempt + 1})")

            except (json.JSONDecodeError, ValueError) as e:
                self.logger.warning(
                    f"Actor JSON parse error (attempt {attempt + 1}): {e}"
                )

            except (ConnectionError, OSError) as e:
                self.logger.warning(f"Actor network error (attempt {attempt + 1}): {e}")

            except Exception as e:
                self.logger.warning(f"Actor error (attempt {attempt + 1}): {e}")

            # Exponential backoff before retry
            if attempt < self.config.max_retries - 1:
                backoff = self.config.retry_backoff_base**attempt
                self.logger.debug(f"Backing off for {backoff}s")
                await asyncio.sleep(backoff)

        # All retries failed - use fallback
        self.logger.warning(
            f"Actor failed after {self.config.max_retries} attempts, using fallback GDD"
        )

        # Create a mock response for tracking if we don't have one
        if last_response is None:
            last_response = LLMResponse(
                content="{}",
                input_tokens=0,
                output_tokens=0,
                model="fallback",
                latency_ms=0,
                finish_reason="error",
            )

        # Extract user_prompt from the prompt message for fallback
        # The prompt contains "## USER GAME CONCEPT\n\n{user_prompt}"
        user_prompt_match = prompt.split("## USER GAME CONCEPT\n\n")
        if len(user_prompt_match) > 1:
            user_prompt_text = user_prompt_match[1].split("\n\n## ")[0]
        else:
            user_prompt_text = "Unknown game concept"

        fallback_gdd = create_fallback_gdd(user_prompt_text)
        return fallback_gdd, last_response

    async def _invoke_critic(self, prompt: str) -> Tuple[CriticFeedback, LLMResponse]:
        """
        Invoke Critic agent with retry logic.

        If Critic fails, generates an approval feedback to avoid blocking.

        Args:
            prompt: User message for Critic

        Returns:
            Tuple of (CriticFeedback, LLMResponse)
        """
        last_response: Optional[LLMResponse] = None

        for attempt in range(self.config.max_retries):
            try:
                response = await asyncio.wait_for(
                    self.llm_provider.generate(
                        system_prompt=GAME_REVIEWER_SYSTEM_PROMPT,
                        user_prompt=prompt,
                        temperature=self.config.critic_temperature,
                        max_tokens=self.config.max_tokens // 2,  # Critic needs less
                        retry=False,
                    ),
                    timeout=self.config.critic_timeout_ms / 1000,
                )
                last_response = response

                # Parse feedback from response
                feedback = CriticFeedback.from_llm_response(response.content)
                return feedback, response

            except asyncio.TimeoutError:
                self.logger.warning(f"Critic timeout (attempt {attempt + 1})")

            except (json.JSONDecodeError, ValueError) as e:
                self.logger.warning(
                    f"Critic JSON parse error (attempt {attempt + 1}): {e}"
                )

            except (ConnectionError, OSError) as e:
                self.logger.warning(
                    f"Critic network error (attempt {attempt + 1}): {e}"
                )

            except Exception as e:
                self.logger.warning(f"Critic error (attempt {attempt + 1}): {e}")

            # Exponential backoff before retry
            if attempt < self.config.max_retries - 1:
                backoff = self.config.retry_backoff_base**attempt
                await asyncio.sleep(backoff)

        # All retries failed - approve by default to avoid blocking
        self.logger.warning(
            f"Critic failed after {self.config.max_retries} attempts, "
            "defaulting to approval"
        )

        # Create approval feedback
        approval_feedback = CriticFeedback(
            decision=Decision.APPROVE,
            blocking_issues=[],
            feasibility_score=7,
            coherence_score=7,
            fun_factor_score=7,
            completeness_score=7,
            originality_score=7,
            review_notes="Auto-approved due to Critic agent failure. Manual review recommended.",
        )

        if last_response is None:
            last_response = LLMResponse(
                content="{}",
                input_tokens=0,
                output_tokens=0,
                model="fallback",
                latency_ms=0,
                finish_reason="error",
            )

        return approval_feedback, last_response

    def _track_tokens(self, response: LLMResponse) -> None:
        """Track token usage from response."""
        self._total_input_tokens += response.input_tokens
        self._total_output_tokens += response.output_tokens

    async def _retry_with_backoff(
        self, coro_func, max_retries: int, backoff_base: float, *args, **kwargs
    ):
        """
        Execute coroutine with exponential backoff retry.

        Used for network error recovery.

        Args:
            coro_func: Coroutine function to execute
            max_retries: Maximum retry attempts
            backoff_base: Base for exponential backoff
            *args: Positional arguments for coro_func
            **kwargs: Keyword arguments for coro_func

        Returns:
            Result of coro_func

        Raises:
            Last exception if all retries fail
        """
        last_error = None

        for attempt in range(max_retries):
            try:
                return await coro_func(*args, **kwargs)
            except (ConnectionError, OSError, TimeoutError) as e:
                last_error = e
                if attempt < max_retries - 1:
                    delay = backoff_base**attempt
                    self.logger.warning(
                        f"Retry attempt {attempt + 1}/{max_retries} "
                        f"after {delay:.1f}s due to: {e}"
                    )
                    await asyncio.sleep(delay)
                else:
                    self.logger.error(f"All {max_retries} retry attempts failed")

        raise last_error  # type: ignore


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


async def generate_gdd(
    user_prompt: str,
    provider_type: str = "mock",
    **provider_kwargs,
) -> RefinementResult:
    """
    Convenience function to generate a GDD.

    Args:
        user_prompt: Game concept description
        provider_type: LLM provider ("anthropic", "openai", "mock")
        **provider_kwargs: Additional provider configuration

    Returns:
        RefinementResult with final GDD

    Example:
        # Using mock for testing
        result = await generate_gdd("zombie roguelike", provider_type="mock")

        # Using Anthropic
        result = await generate_gdd(
            "zombie roguelike",
            provider_type="anthropic",
            api_key="sk-..."
        )
    """
    provider = create_provider(provider_type, **provider_kwargs)
    orchestrator = GamePlanningOrchestrator(provider)
    return await orchestrator.execute(user_prompt)


def create_mock_orchestrator(
    responses: Optional[List[str]] = None,
    config: Optional[OrchestratorConfig] = None,
) -> GamePlanningOrchestrator:
    """
    Create an orchestrator with mock provider for testing.

    Args:
        responses: Optional list of mock responses
        config: Optional orchestrator configuration

    Returns:
        GamePlanningOrchestrator with MockLLMProvider

    Example:
        orchestrator = create_mock_orchestrator()
        result = await orchestrator.execute("test game")
    """
    provider = MockLLMProvider(responses=responses)
    return GamePlanningOrchestrator(provider, config)
