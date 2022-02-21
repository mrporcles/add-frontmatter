# add-frontmatter

This project is written to be used in conjunction with [markdown-to-confluence](https://github.com/vmware-tanzu-labs/markdown-to-confluence).

It will automatically add the required front-matter to relevant Markdown files based on a Jinja2 template.

# Requirements

* Python 3
* A single or set of markdown files to synchronize.

# Installation

To install the project, you need to first install the dependencies:

```sh
pip install -r requirements.txt
```

Alternatively, you can use the provided Docker-file to build a runnable container:

```sh
docker build -t add-frontmatter:v1.0 .
```

This container can then be executed by substituting the mount location of the content directory and executing:

```
docker run -it -v ~/hugo-site:/site add-frontmatter:v1.0 --dir /site
```

# Usage

The script can be run by using the following command once the dependencies have been installed:

```
python3 add-frontmatter.py
```

By default usage parameters will be shown:

```
usage: add-frontmatter.py [-h] [--dir DIR] [--root] [--nobackup] [--dryrun] [posts ...]

Adds required frontmatter to markdown page/s so they can be synced using markdown-to-confluence

positional arguments:
  posts       Individual pages to add frontmatter to

options:
  -h, --help  show this help message and exit
  --dir DIR   The path to your directory containing markdown pages (default: None)
  --root      Sets all base pages parent to be the root page
  --nobackup  Does not create backups of all modified files
  --dryrun    Prints changes that would be made to files without modifying them
```

# Default Front-Matter

A set of default front-matter is added based on the included Jinja2 template. Currently this populates the following:

```yaml
wiki:
    share: true
    parent:
    title:
```

# Options

A couple of configuration options are available based on the parameters passed.

## No Backup

By default every modified markdown file is backed up to the same location with the .bak extension. If you would prefer not to backup these files you can use the --nobackup option.

## Page Hierarchy

By default the base pages titles will be numbered to allow them to be synced to the root of a Confluence space. IE: They will have no parent. If you want them to have a single parent based on the Hugo site name then you can use the --root option.
