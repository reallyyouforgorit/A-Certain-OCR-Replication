# ==========================================
# IMAGE INPAINTING
# ==========================================

import cv2


def inpaint_image(
    image,
    mask,
    radius=3
):
    """
    Menghapus area mask dari image
    menggunakan OpenCV inpainting.
    """

    result = cv2.inpaint(
        image,
        mask,
        radius,
        cv2.INPAINT_TELEA
    )

    return result


def save_image(
    image,
    output_path
):

    success = cv2.imwrite(
        str(output_path),
        image
    )

    if not success:

        raise RuntimeError(
            f"Gagal menyimpan image: {output_path}"
        )