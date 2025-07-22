import os
from pathlib import Path
from PIL import Image, ImageFilter
import shutil


def convert_to_16_9_blur_bg(input_path: Path, output_path: Path):
    with Image.open(input_path) as img:
        img = img.convert("RGB")
        original_width, original_height = img.size
        original_ratio = original_width / original_height
        target_ratio = 16 / 9

        if original_ratio > target_ratio:
            # 横長 → 高さが足りない → 上下に余白
            new_width = original_width
            new_height = int(round(original_width / target_ratio))
        else:
            # 縦長 → 幅が足りない → 左右に余白
            new_height = original_height
            new_width = int(round(original_height * target_ratio))

        # 背景を作る（ぼかし）
        blurred_bg = img.resize((new_width, new_height), Image.LANCZOS)
        blurred_bg = blurred_bg.filter(ImageFilter.GaussianBlur(radius=50))

        # 背景に元画像を貼り付ける
        paste_x = (new_width - original_width) // 2
        paste_y = (new_height - original_height) // 2
        blurred_bg.paste(img, (paste_x, paste_y))

        output_path.parent.mkdir(parents=True, exist_ok=True)
        blurred_bg.save(output_path)
        print(f"✔ Saved: {output_path}")


def batch_convert_folder(folder_path: str):
    input_dir = Path(folder_path)
    if not input_dir.is_dir():
        print(f"❌ 指定されたフォルダが存在しません: {folder_path}")
        return

    output_dir = input_dir.parent / f"{input_dir.name}-converted"

    # 出力フォルダが存在する場合、削除確認
    if output_dir.exists():
        answer = input(f"⚠️ 出力先フォルダ {output_dir} は既に存在します。上書きしてもよいですか？ [y/n]: ").strip().lower()
        if answer == 'y':
            shutil.rmtree(output_dir)
            print(f"🗑 フォルダ内のファイルを削除しました: {output_dir}")
        else:
            print("🚫 処理を中止しました。")
            return

    supported_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')

    for image_file in input_dir.glob("**/*"):
        if image_file.suffix.lower() in supported_extensions:
            relative_path = image_file.relative_to(input_dir)
            output_path = output_dir / relative_path
            convert_to_16_9_blur_bg(image_file, output_path)

    print(f"\n✅ 変換完了！出力フォルダ: {output_dir}")


# 実行例
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("使い方: python convert_16_9.py <画像フォルダのパス>")
    else:
        batch_convert_folder(sys.argv[1])
