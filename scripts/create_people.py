from pathlib import Path
import re
import unicodedata


ARTICLES_DIR = Path("_articles")
PEOPLE_DIR = Path("_people")


def slugify(name: str) -> str:
    """
    Convert a person's name into a clean URL/file slug.
    Example:
    Amir Jadidi -> amir-jadidi
    """

    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")
    name = name.lower().strip()

    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"[\s_]+", "-", name)
    name = re.sub(r"-+", "-", name)

    return name.strip("-")


def extract_front_matter(text: str) -> str | None:
    """
    Return YAML front matter from a Markdown file.
    """

    match = re.match(
        r"^---\s*\n(.*?)\n---",
        text,
        flags=re.DOTALL
    )

    if not match:
        return None

    return match.group(1)


def extract_people(front_matter: str) -> list[str]:
    """
    Read the people field.

    Expected format:
    people: Amir Jadidi, Behrouz Vossoughi, Hamid Nematollah
    """

    match = re.search(
        r"^people:\s*(.+)$",
        front_matter,
        flags=re.MULTILINE
    )

    if not match:
        return []

    value = match.group(1).strip()

    if not value:
        return []

    people = []

    for person in value.split(","):
        person = person.strip()

        if person and person not in people:
            people.append(person)

    return people


def profile_content(name: str) -> str:
    """
    Create the default CinemaDaily person profile.
    """

    return f"""---
layout: person
name: {name}
language: en
title: {name} | News, Films & Updates | CinemaDaily
description: Latest news, projects, career updates and coverage of {name} on CinemaDaily.
---

{name} is covered by CinemaDaily across Iranian cinema, film, television and entertainment news.

This page collects CinemaDaily's latest English-language news, reports and updates about {name}.
"""


def main():
    PEOPLE_DIR.mkdir(parents=True, exist_ok=True)

    if not ARTICLES_DIR.exists():
        print("_articles directory does not exist.")
        return

    discovered_people = []

    for article_path in ARTICLES_DIR.glob("*.md"):
        try:
            text = article_path.read_text(encoding="utf-8")
        except Exception as exc:
            print(f"Could not read {article_path}: {exc}")
            continue

        front_matter = extract_front_matter(text)

        if not front_matter:
            continue

        people = extract_people(front_matter)

        for person in people:
            if person not in discovered_people:
                discovered_people.append(person)

    created = 0

    for name in discovered_people:
        slug = slugify(name)

        if not slug:
            print(f"Skipping invalid person name: {name}")
            continue

        profile_path = PEOPLE_DIR / f"{slug}.md"

        if profile_path.exists():
            print(f"Already exists: {profile_path}")
            continue

        profile_path.write_text(
            profile_content(name),
            encoding="utf-8"
        )

        print(f"Created: {profile_path}")
        created += 1

    print(f"Finished. {created} new profile(s) created.")


if __name__ == "__main__":
    main()
