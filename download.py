import argparse
import requests
import json
from slugify import slugify
import os
from urllib.parse import urlparse


def download(url_base: str, session: str):
    cookies = {"session": session}

    response = requests.get(f"{url_base}/api/v1/challenges", cookies=cookies)
    if response.status_code >= 400:
        print(response.text)
        return

    content = json.loads(response.content.decode("utf-8"))
    for item in content["data"]:
        id = item["id"]
        response = requests.get(f"{url_base}/api/v1/challenges/{id}", cookies=cookies)

        content = json.loads(response.content.decode("utf-8"))["data"]

        name = content["name"]
        description = content["description"]
        category = content["category"]
        tags = content["tags"]

        dir = "base/" + slugify(category) + "/" + slugify(name)
        print(dir)
        if not os.path.isdir(dir):
            os.makedirs(dir)

        if not os.path.isdir(dir + "/input"):
            os.makedirs(dir + "/input")

        if not os.path.isdir(dir + "/solution"):
            os.makedirs(dir + "/solution")

        header = f"# {name}\n"
        tags = ""
        for tag in content["tags"]:
            tags += f"![](https://img.shields.io/badge/{tag}-gray)" + "\n"

        with open(f"{dir}/README.md", "w") as readme_file:
            readme_file.writelines([header, tags, "\n", description])

            if len(content["files"]) > 0:
                readme_file.write("\n\n## Inputs\n")

                for file_path in content["files"]:
                    url = f"{url_base}{file_path}"

                    a = urlparse(url)
                    file_name = os.path.basename(a.path)

                    r = requests.get(url, allow_redirects=True)
                    open(dir + "/input/" + file_name, "wb").write(r.content)
                    readme_file.write(f"- [{file_name}](input/{file_name})\n")

                readme_file.write("\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="CTFd downloader")
    parser.add_argument("-url", type=str, help="e.g. https://ctfd.nki.gov.hu/")
    parser.add_argument("-session", type=str)
    args = parser.parse_args()
    download(args.url, args.session)
