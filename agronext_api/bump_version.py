from pathlib import Path
import toml
from typer import Typer, Option, Exit, echo
 
app = Typer(help="CLI to bump or rollback semantic versions in pyproject.toml under [project].")
 
 
@app.command()
def version(
    patch: bool = Option(False, "--patch", help="Bump or rollback the patch version."),
    minor: bool = Option(False, "--minor", help="Bump or rollback the minor version."),
    major: bool = Option(False, "--major", help="Bump or rollback the major version."),
    rollback: bool = Option(False, "--rollback", help="If set, decrease the specified version part instead of bumping."),
    file: Path = Option(
        Path("pyproject.toml"),
        "-f",
        "--file",
        exists=True,
        readable=True,
        help="Path to the pyproject.toml file containing the version. Defaults to pyproject.toml.",
    ),
):
    """
    Bump or rollback a semantic version (major.minor.patch) under [project].version in pyproject.toml.
    """
    # Ensure exactly one part flag is set
    flags = [patch, minor, major]
    if sum(flags) != 1:
        echo("Error: must specify exactly one of --patch, --minor, or --major.", err=True)
        raise Exit(code=1)
    part = "patch" if patch else "minor" if minor else "major"
 
    # Load TOML
    data = toml.load(file)
 
    # Verify [project].version exists
    project_section = data.get("project")
    if not project_section or "version" not in project_section:
        echo("Error: [project].version not found in the TOML file.", err=True)
        raise Exit(code=1)
 
    current_version = project_section["version"]
    try:
        major_v, minor_v, patch_v = map(int, current_version.split("."))
    except ValueError:
        echo(f"Error: Invalid semantic version format '{current_version}'. Expected 'X.Y.Z'.", err=True)
        raise Exit(code=1)
 
    # Adjust version
    if rollback:
        if part == "major":
            major_v = max(0, major_v - 1)
        elif part == "minor":
            minor_v = max(0, minor_v - 1)
        else:
            patch_v = max(1, patch_v - 1)
    else:
        if part == "major":
            major_v += 1
            minor_v = 0
            patch_v = 0
        elif part == "minor":
            minor_v += 1
            patch_v = 0
        else:
            patch_v += 1
 
    new_version = f"{major_v}.{minor_v}.{patch_v}"
    project_section["version"] = new_version
 
    # Write back
    with file.open("w") as f:
        toml.dump(data, f)
 
    echo(f"Updated version: {current_version} -> {new_version}")
 
 
if __name__ == "__main__":
    app()