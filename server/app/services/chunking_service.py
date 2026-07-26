import re

from app.schemas.chunk_schema import Chunk


class ChunkingService:
    HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$")

    def chunk_document(self, markdown: str) -> list[Chunk]:
        chunks: list[Chunk] = []

        current_heading = ""
        current_level = 0
        current_content: list[str] = []

        lines = markdown.splitlines()

        for line in lines:
            line = line.rstrip()

            heading_match = self.HEADING_PATTERN.match(line)

            if heading_match:
                # Save previous chunk before starting a new section
                if current_heading or any(
                    content.strip() for content in current_content
                ):
                    chunks.append(
                        Chunk(
                            heading=current_heading,
                            level=current_level,
                            content="\n".join(current_content).strip(),
                        )
                    )

                current_level = len(heading_match.group(1))
                current_heading = heading_match.group(2).strip()
                current_content = []

            else:
                current_content.append(line)

        # Save the last chunk
        if current_heading or any(content.strip() for content in current_content):
            chunks.append(
                Chunk(
                    heading=current_heading,
                    level=current_level,
                    content="\n".join(current_content).strip(),
                )
            )

        return chunks
