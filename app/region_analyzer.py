from container_detector import detect_container


def analyze_group(classified_lines):

    container = detect_container(
        classified_lines
    )

    results = []

    for line in classified_lines:

        text_type = line["type"]

        if text_type == "watermark":

            action = "keep"

        elif text_type in [
            "dialogue",
            "narration"
        ]:

            action = "remove_translate"

        else:

            action = "review"

        result = {
            **line,

            "action": action,

            "container_type":
                container["type"],

            "container_box":
                container["box"]
        }

        results.append(result)

    return results