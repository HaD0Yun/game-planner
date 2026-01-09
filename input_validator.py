"""
input_validator.py - 사용자 입력 검증 및 추가 질문 시스템

사용자가 제공한 게임 컨셉이 GDD 생성에 충분한지 검증하고,
부족한 정보가 있으면 추가 질문을 생성합니다.

Usage:
    from input_validator import InputValidator, ValidationResult

    validator = InputValidator()
    result = validator.validate(user_prompt)

    if not result.is_sufficient:
        for question in result.questions:
            print(question)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class InfoCategory(str, Enum):
    """정보 카테고리"""

    GENRE = "genre"
    CORE_CONCEPT = "core_concept"
    PLATFORM = "platform"
    UNIQUE_FEATURE = "unique_feature"
    TARGET_AUDIENCE = "target_audience"
    ART_STYLE = "art_style"
    # 새로 추가된 필수 카테고리
    VIEW_PERSPECTIVE = "view_perspective"  # 2D/3D - 필수!
    ENGINE = "engine"  # 게임 엔진 - 필수!
    MULTIPLAYER_TYPE = "multiplayer_type"  # 솔로/로컬협동/온라인


@dataclass
class ValidationResult:
    """검증 결과"""

    is_sufficient: bool
    questions: List[str] = field(default_factory=list)
    missing_info: List[InfoCategory] = field(default_factory=list)
    detected_info: Dict[InfoCategory, str] = field(default_factory=dict)
    confidence_score: float = 0.0  # 0.0 ~ 1.0

    def get_follow_up_prompt(self) -> str:
        """추가 질문들을 포맷팅된 문자열로 반환"""
        if not self.questions:
            return ""

        lines = ["다음 정보가 필요합니다:\n"]
        for i, q in enumerate(self.questions, 1):
            lines.append(f"{i}. {q}")
        return "\n".join(lines)


# =============================================================================
# 키워드 패턴 정의
# =============================================================================

GENRE_KEYWORDS = {
    "액션": ["액션", "action", "전투", "싸움", "배틀", "격투"],
    "RPG": ["rpg", "롤플레잉", "역할", "레벨업", "스킬트리", "캐릭터 성장"],
    "퍼즐": ["퍼즐", "puzzle", "맞추", "블록", "매치", "두뇌"],
    "시뮬레이션": ["시뮬", "simulation", "경영", "운영", "관리", "타이쿤"],
    "로그라이크": ["로그라이크", "roguelike", "roguelite", "랜덤", "던전", "퍼마데스"],
    "플랫포머": ["플랫포머", "platformer", "점프", "달리기", "마리오"],
    "슈팅": ["슈팅", "shooting", "shooter", "총", "발사", "탄막"],
    "어드벤처": ["어드벤처", "adventure", "탐험", "모험", "스토리"],
    "호러": ["호러", "horror", "공포", "무서운", "괴물"],
    "생존": ["생존", "survival", "서바이벌", "살아남"],
    "레이싱": ["레이싱", "racing", "경주", "자동차", "드라이브"],
    "스포츠": ["스포츠", "sports", "축구", "야구", "농구"],
    "격투": ["격투", "fighting", "대전", "1:1"],
    "샌드박스": ["샌드박스", "sandbox", "자유", "창작", "건설"],
    "리듬": ["리듬", "rhythm", "음악", "박자", "노래"],
    "카드": ["카드", "card", "덱빌딩", "TCG", "CCG"],
    "타워디펜스": ["타워디펜스", "tower defense", "방어", "웨이브"],
    "방치형": ["방치", "idle", "클리커", "자동"],
    "힐링": ["힐링", "healing", "편안", "relaxing", "cozy", "따뜻"],
}

PLATFORM_KEYWORDS = {
    "PC": ["pc", "컴퓨터", "스팀", "steam", "데스크톱"],
    "웹": ["웹", "web", "브라우저", "browser", "html"],
    "모바일": ["모바일", "mobile", "스마트폰", "폰", "ios", "android", "앱"],
    "콘솔": [
        "콘솔",
        "console",
        "플스",
        "엑박",
        "스위치",
        "playstation",
        "xbox",
        "nintendo",
    ],
    "VR": ["vr", "가상현실", "virtual reality", "오큘러스"],
}

ART_STYLE_KEYWORDS = {
    "픽셀아트": ["픽셀", "pixel", "도트", "8bit", "16bit", "레트로"],
    "카툰": ["카툰", "cartoon", "만화풍", "애니"],
    "리얼리스틱": ["리얼", "realistic", "사실적", "실사"],
    "미니멀": ["미니멀", "minimal", "심플", "단순"],
    "손그림": ["손그림", "hand drawn", "일러스트", "수채화"],
    "스타일라이즈드": ["stylized", "스타일라이즈", "양식화"],
    "로우폴리": ["low poly", "로우폴리", "저폴리"],
}

# ============================================================================
# 새로 추가: 2D/3D 시점 키워드 (필수!)
# ============================================================================
VIEW_PERSPECTIVE_KEYWORDS = {
    "3D": [
        "3d",
        "삼차원",
        "3인칭",
        "1인칭",
        "third person",
        "first person",
        "tps",
        "fps",
        "폴리곤",
        "유니티",
        "unity",
        "언리얼",
        "unreal",
        "3d 플랫포머",
        "오픈월드",
        "open world",
    ],
    "2D": [
        "2d",
        "이차원",
        "사이드뷰",
        "side view",
        "탑다운",
        "top down",
        "횡스크롤",
        "픽셀",
        "스프라이트",
        "도트",
        "2d 플랫포머",
        "메트로베니아",
        "metroidvania",
    ],
    "2.5D": ["2.5d", "이소메트릭", "isometric", "쿼터뷰", "quarter view"],
}

# ============================================================================
# 새로 추가: 게임 엔진 키워드 (필수!)
# ============================================================================
ENGINE_KEYWORDS = {
    "Unity": ["unity", "유니티"],
    "Unreal": ["unreal", "언리얼", "ue4", "ue5"],
    "Godot": ["godot", "고도", "고돗"],
    "GameMaker": ["gamemaker", "game maker", "gms", "gms2"],
    "Pygame": ["pygame", "파이게임"],
    "Phaser": ["phaser", "페이저"],
    "Love2D": ["love2d", "löve", "love 2d"],
    "RPG Maker": ["rpg maker", "rpg메이커", "rpgmaker", "알만툴"],
    "Construct": ["construct", "컨스트럭트"],
    "Custom": ["자체 엔진", "custom engine", "직접 개발"],
}

# ============================================================================
# 새로 추가: 멀티플레이어 유형 키워드
# ============================================================================
MULTIPLAYER_KEYWORDS = {
    "솔로": ["싱글", "single", "solo", "1인", "혼자", "싱글플레이어"],
    "로컬협동": [
        "로컬",
        "local",
        "협동",
        "co-op",
        "coop",
        "2인",
        "2p",
        "같이",
        "함께",
        "couch",
        "split screen",
        "분할 화면",
        "로컬 멀티",
        "local multi",
    ],
    "온라인": [
        "온라인",
        "online",
        "멀티플레이어",
        "multiplayer",
        "pvp",
        "대전",
        "매칭",
        "서버",
        "네트워크",
    ],
}


class InputValidator:
    """사용자 입력 검증기"""

    # 최소 충분 점수 (이 이상이면 GDD 생성 가능)
    # 0.6으로 상향 - 필수 정보가 더 많이 필요함
    MIN_SUFFICIENT_SCORE = 0.6

    # 필수 카테고리 - 이것들이 없으면 무조건 질문
    REQUIRED_CATEGORIES = [
        InfoCategory.GENRE,
        InfoCategory.CORE_CONCEPT,
        InfoCategory.VIEW_PERSPECTIVE,  # 2D/3D 필수!
        InfoCategory.ENGINE,  # 엔진 필수!
    ]

    def __init__(self):
        self.genre_patterns = self._compile_patterns(GENRE_KEYWORDS)
        self.platform_patterns = self._compile_patterns(PLATFORM_KEYWORDS)
        self.art_style_patterns = self._compile_patterns(ART_STYLE_KEYWORDS)
        self.view_patterns = self._compile_patterns(VIEW_PERSPECTIVE_KEYWORDS)
        self.engine_patterns = self._compile_patterns(ENGINE_KEYWORDS)
        self.multiplayer_patterns = self._compile_patterns(MULTIPLAYER_KEYWORDS)

    def _compile_patterns(
        self, keyword_dict: Dict[str, List[str]]
    ) -> Dict[str, re.Pattern]:
        """키워드를 정규식 패턴으로 컴파일"""
        patterns = {}
        for category, keywords in keyword_dict.items():
            pattern = "|".join(re.escape(kw) for kw in keywords)
            patterns[category] = re.compile(pattern, re.IGNORECASE)
        return patterns

    def _detect_genre(self, text: str) -> Optional[str]:
        """장르 감지"""
        for genre, pattern in self.genre_patterns.items():
            if pattern.search(text):
                return genre
        return None

    def _detect_platform(self, text: str) -> Optional[str]:
        """플랫폼 감지"""
        for platform, pattern in self.platform_patterns.items():
            if pattern.search(text):
                return platform
        return None

    def _detect_art_style(self, text: str) -> Optional[str]:
        """아트 스타일 감지"""
        for style, pattern in self.art_style_patterns.items():
            if pattern.search(text):
                return style
        return None

    def _detect_view_perspective(self, text: str) -> Optional[str]:
        """2D/3D 시점 감지 - 필수!"""
        for view, pattern in self.view_patterns.items():
            if pattern.search(text):
                return view
        return None

    def _detect_engine(self, text: str) -> Optional[str]:
        """게임 엔진 감지 - 필수!"""
        for engine, pattern in self.engine_patterns.items():
            if pattern.search(text):
                return engine
        return None

    def _detect_multiplayer_type(self, text: str) -> Optional[str]:
        """멀티플레이어 유형 감지"""
        for mp_type, pattern in self.multiplayer_patterns.items():
            if pattern.search(text):
                return mp_type
        return None

    def _has_core_concept(self, text: str) -> bool:
        """핵심 게임 컨셉이 있는지 확인"""
        # 최소 단어 수 체크
        words = text.split()
        if len(words) < 3:
            return False

        # 게임 관련 동사나 명사가 있는지
        game_verbs = [
            "키우",
            "싸우",
            "만들",
            "수집",
            "탐험",
            "생존",
            "달리",
            "점프",
            "쏘",
            "방어",
            "공격",
            "해결",
            "찾",
            "모으",
            "성장",
            "관리",
            "build",
            "fight",
            "collect",
            "explore",
            "survive",
            "run",
            "jump",
            "shoot",
            "defend",
            "attack",
            "solve",
            "find",
            "grow",
            "manage",
        ]

        text_lower = text.lower()
        for verb in game_verbs:
            if verb in text_lower:
                return True

        return len(words) >= 5  # 최소 5단어면 일단 컨셉 있다고 봄

    def _has_unique_feature(self, text: str) -> bool:
        """독특한 특징이 언급되었는지 확인"""
        # 특별한 메카닉이나 특징을 나타내는 표현
        unique_indicators = [
            "특별",
            "독특",
            "새로운",
            "유니크",
            "다른",
            "특이",
            "unique",
            "special",
            "new",
            "different",
            "twist",
            "~이",
            "~가",
            "~를",
            "~을",  # 구체적 명사를 수식하는 조사
        ]

        text_lower = text.lower()
        for indicator in unique_indicators:
            if indicator in text_lower:
                return True

        # 구체적인 메카닉 설명이 있는지 (예: "~하면 ~된다", "~을 통해")
        mechanic_patterns = [
            r".+하면.+",
            r".+통해.+",
            r".+으로.+",
            r".+기능",
            r".+시스템",
        ]

        for pattern in mechanic_patterns:
            if re.search(pattern, text):
                return True

        return False

    def validate(self, user_prompt: str) -> ValidationResult:
        """
        사용자 입력을 검증하고 부족한 정보에 대한 질문을 생성합니다.

        Args:
            user_prompt: 사용자가 입력한 게임 컨셉

        Returns:
            ValidationResult: 검증 결과 (충분 여부, 질문 목록, 감지된 정보)
        """
        detected_info: Dict[InfoCategory, str] = {}
        missing_info: List[InfoCategory] = []
        questions: List[str] = []

        # 입력이 너무 짧은 경우
        if len(user_prompt.strip()) < 5:
            return ValidationResult(
                is_sufficient=False,
                questions=[
                    "게임 컨셉을 더 자세히 설명해 주세요. 어떤 게임을 만들고 싶으신가요?"
                ],
                missing_info=[InfoCategory.CORE_CONCEPT],
                detected_info={},
                confidence_score=0.0,
            )

        # ================================================================
        # 1. 장르 감지 (필수)
        # ================================================================
        genre = self._detect_genre(user_prompt)
        if genre:
            detected_info[InfoCategory.GENRE] = genre
        else:
            missing_info.append(InfoCategory.GENRE)
            questions.append(
                "🎮 [필수] 어떤 장르의 게임인가요? (예: 액션, RPG, 퍼즐, 플랫포머, 로그라이크, 슈팅 등)"
            )

        # ================================================================
        # 2. 핵심 컨셉 확인 (필수)
        # ================================================================
        if self._has_core_concept(user_prompt):
            detected_info[InfoCategory.CORE_CONCEPT] = "detected"
        else:
            missing_info.append(InfoCategory.CORE_CONCEPT)
            questions.append(
                "🎯 [필수] 게임의 핵심 플레이 방식은 무엇인가요? (예: 무엇을 하고, 어떻게 진행되나요?)"
            )

        # ================================================================
        # 3. 2D/3D 시점 감지 (필수!) - 새로 추가
        # ================================================================
        view = self._detect_view_perspective(user_prompt)
        if view:
            detected_info[InfoCategory.VIEW_PERSPECTIVE] = view
        else:
            missing_info.append(InfoCategory.VIEW_PERSPECTIVE)
            questions.append(
                "🖼️ [필수] 게임의 시점은 무엇인가요? (예: 3D 1인칭, 3D 3인칭, 2D 사이드뷰, 2D 탑다운, 2.5D 이소메트릭)"
            )

        # ================================================================
        # 4. 게임 엔진 감지 (필수!) - 새로 추가
        # ================================================================
        engine = self._detect_engine(user_prompt)
        if engine:
            detected_info[InfoCategory.ENGINE] = engine
        else:
            missing_info.append(InfoCategory.ENGINE)
            questions.append(
                "🔧 [필수] 어떤 게임 엔진을 사용하나요? (예: Unity, Unreal, Godot, GameMaker, 웹/HTML5)"
            )

        # ================================================================
        # 5. 플랫폼 감지 (선택)
        # ================================================================
        platform = self._detect_platform(user_prompt)
        if platform:
            detected_info[InfoCategory.PLATFORM] = platform

        # ================================================================
        # 6. 아트 스타일 감지 (선택)
        # ================================================================
        art_style = self._detect_art_style(user_prompt)
        if art_style:
            detected_info[InfoCategory.ART_STYLE] = art_style

        # ================================================================
        # 7. 멀티플레이어 유형 감지 (선택) - 새로 추가
        # ================================================================
        multiplayer = self._detect_multiplayer_type(user_prompt)
        if multiplayer:
            detected_info[InfoCategory.MULTIPLAYER_TYPE] = multiplayer

        # ================================================================
        # 8. 독특한 특징 확인 (선택)
        # ================================================================
        if self._has_unique_feature(user_prompt):
            detected_info[InfoCategory.UNIQUE_FEATURE] = "detected"

        # ================================================================
        # 신뢰도 점수 계산
        # ================================================================
        # 필수 카테고리 충족 여부 체크
        required_met = sum(
            1 for cat in self.REQUIRED_CATEGORIES if cat in detected_info
        )
        required_total = len(self.REQUIRED_CATEGORIES)

        # 전체 카테고리 (8개)
        total_categories = 8
        detected_count = len(detected_info)

        # 기본 점수 = 감지된 정보 비율
        base_score = detected_count / total_categories

        # 필수 정보 보너스/페널티
        required_ratio = required_met / required_total
        confidence_score = (base_score * 0.4) + (required_ratio * 0.6)

        # ================================================================
        # 충분 여부 결정 - 필수 카테고리가 모두 있어야 함!
        # ================================================================
        all_required_met = all(cat in detected_info for cat in self.REQUIRED_CATEGORIES)
        is_sufficient = (
            all_required_met and confidence_score >= self.MIN_SUFFICIENT_SCORE
        )

        # 선택적 질문 추가 (필수가 충족되었지만 추가 정보 권장)
        if all_required_met and not is_sufficient:
            if InfoCategory.PLATFORM not in detected_info:
                questions.append(
                    "📱 [권장] 타겟 플랫폼이 있나요? (예: PC, 모바일, 웹, 콘솔)"
                )
            if InfoCategory.MULTIPLAYER_TYPE not in detected_info:
                questions.append(
                    "👥 [권장] 싱글플레이인가요, 멀티플레이인가요? (예: 솔로, 로컬 협동, 온라인)"
                )

        return ValidationResult(
            is_sufficient=is_sufficient,
            questions=questions,
            missing_info=missing_info,
            detected_info=detected_info,
            confidence_score=confidence_score,
        )

    def enhance_prompt(
        self, original_prompt: str, additional_info: Dict[str, str]
    ) -> str:
        """
        추가 정보를 반영하여 프롬프트를 보강합니다.

        Args:
            original_prompt: 원래 사용자 입력
            additional_info: 추가로 수집한 정보 (질문 응답)

        Returns:
            보강된 프롬프트
        """
        enhanced_parts = [original_prompt]

        for key, value in additional_info.items():
            if value.strip():
                enhanced_parts.append(f"{key}: {value}")

        return "\n".join(enhanced_parts)


# =============================================================================
# CLI 통합용 헬퍼 함수
# =============================================================================


def validate_and_ask(prompt: str, console: Any = None) -> tuple[bool, str]:
    """
    프롬프트를 검증하고 필요시 추가 질문을 합니다.

    Args:
        prompt: 사용자 입력 프롬프트
        console: Rich Console 객체 (없으면 print 사용)

    Returns:
        (성공 여부, 최종 프롬프트 또는 에러 메시지)
    """
    validator = InputValidator()
    result = validator.validate(prompt)

    if result.is_sufficient:
        return True, prompt

    # 질문 출력
    if console:
        from rich.panel import Panel

        console.print()
        console.print(
            Panel(
                result.get_follow_up_prompt(),
                title="추가 정보 필요",
                border_style="yellow",
            )
        )
    else:
        print("\n" + result.get_follow_up_prompt())

    return False, result.get_follow_up_prompt()


def interactive_validate(prompt: str) -> str:
    """
    대화형으로 프롬프트를 검증하고 필요한 정보를 수집합니다.

    Args:
        prompt: 초기 사용자 입력

    Returns:
        보강된 최종 프롬프트
    """
    validator = InputValidator()
    result = validator.validate(prompt)

    if result.is_sufficient:
        return prompt

    additional_info = {}

    print("\n" + "=" * 50)
    print("추가 정보가 필요합니다.")
    print("=" * 50 + "\n")

    for question in result.questions:
        answer = input(f"{question}\n> ").strip()
        if answer:
            # 질문 키워드로 분류
            if "장르" in question:
                additional_info["장르"] = answer
            elif "플레이" in question or "방식" in question:
                additional_info["핵심 플레이"] = answer
            elif "시점" in question or "2D" in question or "3D" in question:
                additional_info["시점"] = answer  # 2D/3D
            elif "엔진" in question:
                additional_info["게임 엔진"] = answer
            elif "플랫폼" in question:
                additional_info["플랫폼"] = answer
            elif "멀티" in question or "싱글" in question or "협동" in question:
                additional_info["플레이 유형"] = answer
            elif "특별" in question or "차별" in question:
                additional_info["특징"] = answer
            else:
                additional_info["추가 정보"] = answer

    return validator.enhance_prompt(prompt, additional_info)
