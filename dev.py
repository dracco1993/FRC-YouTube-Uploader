import subprocess


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
    name = "input.mkv"
    times = []
    times.append(["00:00:00", "00:00:10"])
    times.append(["00:06:00", "00:07:00"])
    # times = [["00:00:00", get_duration(name)]]
    if len(times) == 1:
        time = times[0]
        cmd = [
            "ffmpeg",
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
            "output.mp4",
        ]
        subprocess.check_output(cmd)
    else:
        open("concatenate.txt", "w").close()
        for idx, time in enumerate(times):
            output_filename = f"output{idx}.mp4"
            cmd = [
                "ffmpeg",
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
                output_filename,
            ]
            subprocess.check_output(cmd)

            with open("concatenate.txt", "a") as myfile:
                myfile.write(f"file {output_filename}\n")

        cmd = [
            "ffmpeg",
            "-f",
            "concat",
            "-i",
            "concatenate.txt",
            "-c",
            "copy",
            "output.mp4",
        ]
        output = subprocess.check_output(cmd).decode("utf-8").strip()
        print(output)


if __name__ == "__main__":
    main()
