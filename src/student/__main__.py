import fire

from student.models import Chunk


class CLI:
    def test_model(self) -> None:
        chunk = Chunk(
            chunk_id="1",
            file_path="example.py",
            file_type="python",
            text="print('hello')",
            first_character_index=0,
            last_character_index=14,
        )

        print(chunk.model_dump_json(indent=2))


if __name__ == "__main__":
    fire.Fire(CLI)
