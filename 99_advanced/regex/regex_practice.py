import re

print("### 1. 기본 메타문자 ###")
tests = [
    (r".", "a", "임의의 문자 1개 (줄바꿈 제외)"),
    (r"^Hello", "Hello world", "문자열 시작"),
    (r"world$", "Hello world", "문자열 끝"),
    (r"a*", "aaab", "a가 0개 이상"),
    (r"a+", "aaab", "a가 1개 이상"),
    (r"a?", "b", "a가 0개 또는 1개"),
    (r"a{2,3}", "aaaa", "a가 2~3개"),
]
for pattern, text, desc in tests:
    m = re.search(pattern, text)
    print(f"  {desc:25} pattern={pattern!r:12} text={text!r:15} -> {m.group() if m else None}")

print()
print("### 2. 문자 클래스 ###")
tests2 = [
    (r"[abc]", "cat", "a,b,c 중 하나"),
    (r"[^abc]", "cat", "a,b,c가 아닌 것"),
    (r"[a-z]", "Cat", "소문자 범위"),
    (r"[A-Za-z0-9]", "!@#Ab3", "영문+숫자"),
    (r"\d", "abc123", "숫자 (=[0-9])"),
    (r"\D", "abc123", "숫자 아님"),
    (r"\w", "hi_23!", "단어문자(영문/숫자/_)"),
    (r"\W", "hi_23!", "단어문자 아님"),
    (r"\s", "a b\tc", "공백문자"),
]
for pattern, text, desc in tests2:
    m = re.search(pattern, text)
    print(f"  {desc:20} pattern={pattern!r:8} text={text!r:12} -> {m.group() if m else None}")

print()
print("### 3. 그룹과 캡처 ###")
m = re.search(r"(\d{4})-(\d{2})-(\d{2})", "2026-08-22")
print("  전체:", m.group(0), "| 그룹들:", m.groups())  # type: ignore

m2 = re.search(r"(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})", "2026-08-22")
print("  이름 그룹:", m2.groupdict())  # type: ignore

m3 = re.search(r"(?:\d{4})-(\d{2})", "2026-08")
print("  비캡처 그룹 (?:...) - groups():", m3.groups())  # 비캡처는 그룹에서 제외됨 # type: ignore

print()
print("### 4. 수량자(quantifier) 탐욕 vs 게으름 ###")
text = "<a><b>"
greedy = re.search(r"<.+>", text)
lazy = re.search(r"<.+?>", text)
print("  탐욕적(greedy)  <.+>  :", greedy.group())  # type: ignore
print("  게으른(lazy)   <.+?> :", lazy.group())  # type: ignore

print()
print("### 5. 앵커와 경계 ###")
print("  \\b (단어 경계):", re.findall(r"\bcat\b", "cat category cats cat"))
print("  \\B (단어 경계 아님):", re.findall(r"\Bcat", "concatenate"))

print()
print("### 6. lookahead / lookbehind ###")
# 긍정 전방탐색: 뒤에 특정 패턴이 있어야 매칭 (그 패턴 자체는 소비 안함)
print("  긍정 전방탐색 (?=원)：", re.findall(r"\d+(?=원)", "가격 1000원, 무게 5kg"))
# 부정 전방탐색
print("  부정 전방탐색 (?!원)：", re.findall(r"\d+(?!원)", "가격 1000원, 무게 5kg"))
# 긍정 후방탐색: 앞에 특정 패턴이 있어야 매칭
print("  긍정 후방탐색 (?<=\\$)：", re.findall(r"(?<=\$)\d+", "가격은 $500 입니다"))
# 부정 후방탐색
print("  부정 후방탐색 (?<!\\$)：", re.findall(r"(?<!\$)\b\d+\b", "가격 $500, 수량 3"))

print()
print("### 7. 플래그(flags) ###")
print("  IGNORECASE:", re.findall(r"hello", "Hello HELLO hello", re.IGNORECASE))
text_multi = "line1\nline2\nline3"
print("  MULTILINE (^매칭 각 줄):", re.findall(r"^line\d", text_multi, re.MULTILINE))
print("  DOTALL (.이 줄바꿈도 포함):", re.search(r"line1.line2", text_multi, re.DOTALL).group())  # type: ignore

print()
print("### 8. re.compile 재사용 ###")
PHONE = re.compile(r"01\d-\d{3,4}-\d{4}")
for t in ["010-1234-5678", "011-123-4567", "abc"]:
    m = PHONE.match(t)
    print(f"  {t:15} -> {'매칭: ' + m.group() if m else '매칭 안됨'}")

for m in PHONE.finditer("010-1234-5678"):
    n = int(m.group(1))  # 캡처 그룹 1번 (괄호 안 숫자) 을 정수로 변환

print()
print("### 9. sub / subn (치환) ###")
print("  sub:", re.sub(r"\d+", "#", "a1b22c333"))
print("  subn (치환+개수):", re.subn(r"\d+", "#", "a1b22c333"))
print("  count 제한:", re.sub(r"\d+", "#", "a1b22c333", count=1))

print()
print("### 10. split (분리) ###")
print("  기본:", re.split(r",\s*", "a, b,  c,d"))
print("  maxsplit:", re.split(r",\s*", "a, b,  c,d", maxsplit=1))
print("  캡처그룹 포함 split은 구분자도 결과에 포함:", re.split(r"(,)", "a,b,c"))

print()
print("### 11. 이스케이프가 필요한 특수문자 ###")
print("  마침표 리터럴:", re.findall(r"\.", "3.14"))
print("  괄호 리터럴:", re.findall(r"\(.*?\)", "함수(인자1, 인자2) 호출"))

print()
print("### 12. 자주 틀리는 실수 ###")
# 실수1: r"" (raw string) 안 쓰면 \d가 이스케이프 시퀀스로 오인될 수 있음
print("  \\d 는 raw string 없이도 우연히 동작(파이썬에 \\d 이스케이프가 없어서):", re.findall(r"\d", "abc123"))
# 실수2: findall에 그룹이 있으면 전체매칭이 아니라 그룹만 반환됨
only_group = re.findall(r"(\d+)원", "1000원, 2000원")
print("  그룹 있는 findall -> 그룹값만 반환:", only_group)
no_group = re.findall(r"\d+원", "1000원, 2000원")
print("  그룹 없는 findall -> 전체매칭 반환:", no_group)
