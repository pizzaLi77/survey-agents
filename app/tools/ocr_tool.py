from app.schemas.medical_record import ImageInfo, OcrResult


class OcrTool:
    async def recognize(self, images: list[ImageInfo]) -> list[OcrResult]:
        return [
            OcrResult(
                image_id=image.image_id,
                text=(
                    f"{image.image_name or image.image_id} OCR：南京市第一人民医院，"
                    "张三于2024-05-20至2024-05-25在心内科住院，"
                    "主诉胸闷3天，诊断为冠心病。现病史记载活动后胸闷，既往史高血压5年。"
                ),
                confidence=0.92,
            )
            for image in images
        ]
