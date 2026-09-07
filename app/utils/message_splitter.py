from typing import List


def split_text(text: str, max_length: int = 4000) -> List[str]:
    """
    Telegram xabar uzunligi cheklovi (4096 belgi) uchun matnni xavfsiz bo'lib berish.
    Paragraflar bo'yicha yoki bo'shliqlar bo'yicha uzilishlar hosil qiladi.
    """
    if not text:
        return [""]

    if len(text) <= max_length:
        return [text]

    chunks: List[str] = []
    lines = text.split("\n")
    current_chunk = ""

    for line in lines:
        if len(current_chunk) + len(line) + 1 <= max_length:
            if current_chunk:
                current_chunk += "\n" + line
            else:
                current_chunk = line
        else:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""

            # Agar bitta qatorning o'zi max_length dan uzun bo'lsa
            if len(line) > max_length:
                start = 0
                while start < len(line):
                    chunks.append(line[start:start + max_length])
                    start += max_length
            else:
                current_chunk = line

    if current_chunk:
        chunks.append(current_chunk)

    return chunks
