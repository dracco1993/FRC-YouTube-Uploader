import subprocess

FOLDER = "videos"

def get_duration(input_video):
    cmd = [
        "ffprobe",
        "-i",
        input_video,
        "-show_entries",
        "format=duration",
        "-v",
        "quiet",
        "-sexagesimal",
        "-of",
        "csv=p=0",
    ]
    return subprocess.check_output(cmd).decode("utf-8").strip()


def main():
    name = f"{FOLDER}/stream.mp4"
    times = []
    times.append(["00:00:00", "00:00:5"])
    times.append(["00:00:10", "00:00:20"])
    # times = [["00:00:00", get_duration(name)]]
    if len(times) == 1:
        time = times[0]
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            name,
            "-ss",
            time[0],
            "-to",
            time[1],
            "-c:v",
            "copy",
            "-c:a",
            "copy",
            "{FOLDER}/output.mp4",
        ]
        subprocess.check_output(cmd)
    else:
        open(f"{FOLDER}/concatenate.txt", "w").close()
        for idx, time in enumerate(times):
            output_filename = f"output{idx}.mp4"
            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                name,
                "-ss",
                time[0],
                "-to",
                time[1],
                "-c:v",
                "copy",
                "-c:a",
                "copy",
                f"{FOLDER}/{output_filename}",
            ]
            subprocess.check_output(cmd)

            with open(f"{FOLDER}/concatenate.txt", "a") as myfile:
                myfile.write(f"file {output_filename}\n")

        cmd = [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-i",
            f"{FOLDER}/concatenate.txt",
            "-c",
            "copy",
            f"{FOLDER}/output.mp4",
        ]
        output = subprocess.check_output(cmd).decode("utf-8").strip()
        print(output)


if __name__ == "__main__":
    main()
