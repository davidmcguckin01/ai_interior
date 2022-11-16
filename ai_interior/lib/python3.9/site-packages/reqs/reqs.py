import asyncio
import os
import re
import sys
from typing import Dict, List

import httpx

REGEXP = re.compile(
    r"(?P<opt>\s*(-|--).*[^ #])*(?P<pkg>^[^- #][\w-]+)*(?P<sigver>\s*(?P<sig>~=|==|!=|<=|>=|<|>|===)+\s*(?P<ver>[\d.*]+)\s*)*(?P<env>;.*)*(?P=opt)*(?P<com>\s*#.*)*"
)


async def read_file(path: str) -> List[Dict[str, str]]:
    assert isinstance(path, str)
    assert os.path.isfile(path)
    assert path.endswith(".txt")  # todo: maybe remove it
    result = []
    with open(path, "r") as file:
        lines = file.readlines()
        for line in lines:
            line = await parse_line(line)
            result.append(line)
    return result


async def parse_line(line: str) -> Dict[str, str]:
    match = re.match(REGEXP, line)
    result = match.groupdict()
    return result


async def adjust_signs(line: Dict[str, str], sign: str = "==") -> Dict[str, str]:
    if not line["sigver"]:
        line["sig"] = sign if line["pkg"] and line["ver"] else None
    return line


async def create_links(lines: List[Dict[str, str]]) -> List[Dict[str, str]]:
    assert isinstance(lines, list)
    for line in lines:
        if line["pkg"] and not line["sigver"]:
            line["link"] = f"https://pypi.python.org/pypi/{line['pkg']}/json"
    return lines


async def get_link(line: Dict[str, str]) -> Dict[str, str]:
    assert isinstance(line, dict)
    try:
        link = line["link"]
        async with httpx.AsyncClient() as client:
            r = await client.get(link)
        info = r.json()
    except Exception as e:
        print(f"{e.__class__.__name__}: {e}, {line}")
    else:
        info = info.get("info", None)
        if info:
            line["pkg"] = info["name"]
            line["ver"] = info["version"]
    return line


async def download_info(lines: List[Dict[str, str]]) -> List[Dict[str, str]]:
    assert isinstance(lines, list)
    tasks = [get_link(line) for line in lines]
    result = await asyncio.gather(*tasks)
    result = [r for r in result if r is not None]
    return result


async def prepare_reqs(lines: List[Dict[str, str]], sign: str = "==") -> List[str]:
    assert isinstance(lines, list)
    assert isinstance(sign, str)
    result = []
    for line in lines:
        line = await adjust_signs(line, sign)
        if line["pkg"] or line["com"]:
            result.append(
                f"{line['pkg'] or ''}{line['sig'] or ''}{line['ver'] or ''}{line['env'] or ''}{line['com'] or ''}"
            )
        elif line["opt"]:
            result.append(f"{line['opt']}{line['com'] or ''}")
        else:
            result.append("")
    return result


async def write_file(path: str, reqs: List[str]) -> None:
    assert isinstance(path, str)
    assert isinstance(reqs, list)
    with open(path, "w") as file:
        to_write = "\n".join(reqs)
        file.write(to_write)


async def find_requirements(path: str) -> list:
    result = []
    for dirpath, _, filenames in os.walk(path):
        for file in filenames:
            if file.startswith("requirements"):
                result.append(os.path.join(dirpath, file))
    return result


async def run(path: str) -> None:
    assert isinstance(path, str)
    files = await find_requirements(path)
    for file in files:
        content = await read_file(file)
        links = await create_links(content)
        info = await download_info(links)
        reqs = await prepare_reqs(info)
        await write_file(file, reqs)
        print(file)


def main():
    try:
        path = sys.argv[1]
    except IndexError:
        print("Enter path to file")
        path = input()
    else:
        asyncio.run(run(path))


if __name__ == "__main__":
    main()
