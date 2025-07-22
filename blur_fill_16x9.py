import os
from pathlib import Path
from PIL import Image, ImageFilter
import shutil


def convert_to_16_9_blur_bg(input_path: Path, output_path: Path, output_format: str = "PNG", quality: int = 95):
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

        # フォーマットに応じて保存オプションを設定
        save_kwargs = {}
        if output_format.upper() == "JPEG":
            save_kwargs = {"quality": quality, "optimize": True}
        elif output_format.upper() == "WEBP":
            save_kwargs = {"quality": quality, "method": 6}  # method=6は最高品質
        elif output_format.upper() == "PNG":
            save_kwargs = {"optimize": True}

        blurred_bg.save(output_path, format=output_format, **save_kwargs)
        print(f"✔ Saved: {output_path} (format: {output_format}, quality: {quality if output_format.upper() != 'PNG' else 'lossless'})")


def batch_convert_folder(folder_path: str, output_format: str = "PNG", quality: int = 95):
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

    # 出力ファイルの拡張子を決定
    format_extensions = {
        "PNG": ".png",
        "JPEG": ".jpg",
        "WEBP": ".webp"
    }
    output_ext = format_extensions.get(output_format.upper(), ".png")

    for image_file in input_dir.glob("**/*"):
        if image_file.suffix.lower() in supported_extensions:
            relative_path = image_file.relative_to(input_dir)
            # 出力ファイルの拡張子を変更
            output_path = output_dir / relative_path.with_suffix(output_ext)
            convert_to_16_9_blur_bg(image_file, output_path, output_format, quality)

    print(f"\n✅ 変換完了！出力フォルダ: {output_dir}")
    print(f"📊 出力フォーマット: {output_format} (品質: {quality if output_format.upper() != 'PNG' else 'ロスレス'})")


# 実行例
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("使い方:")
        print("  python blur_fill_16x9.py <画像フォルダのパス>")
        print("  python blur_fill_16x9.py <画像フォルダのパス> <フォーマット> [品質]")
        print("")
        print("フォーマット: PNG (デフォルト・ロスレス), WEBP (高効率), JPEG")
        print("品質: 1-100 (JPEGとWebPのみ、デフォルト95)")
        print("")
        print("例:")
        print("  python blur_fill_16x9.py ./photos")
        print("  python blur_fill_16x9.py ./photos WEBP 95")
        print("  python blur_fill_16x9.py ./photos JPEG 98")
        print("  python blur_fill_16x9.py ./photos PNG")
    else:
        folder_path = sys.argv[1]
        output_format = sys.argv[2].upper() if len(sys.argv) > 2 else "PNG"
        quality = int(sys.argv[3]) if len(sys.argv) > 3 else 95

        # フォーマット検証
        if output_format not in ["PNG", "JPEG", "WEBP"]:
            print(f"❌ サポートされていないフォーマット: {output_format}")
            print("サポート形式: PNG, JPEG, WEBP")
            sys.exit(1)

        # 品質検証
        if not (1 <= quality <= 100):
            print(f"❌ 品質は1-100の範囲で指定してください: {quality}")
            sys.exit(1)

        print(f"🔧 設定: フォーマット={output_format}, 品質={quality if output_format != 'PNG' else 'ロスレス'}")
        batch_convert_folder(folder_path, output_format, quality)
