#!/usr/bin/env python3

import argparse
import logging
import os
import sys
import frontmatter
import shutil

from glob import glob
from pathlib import Path
from editfrontmatter import EditFrontMatter

"""Adds frontmatter to markdown file/s in a specified location

This script is meant to be executed on a base Hugo site and would
usually be used as a precursor to markdown-to-confluence
"""

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)

parentlist = []
skippedpages = []

title_list = []
num_title_list = []


SUPPORTED_FORMATS = ['.md']
DIFF_FILES = ['.diff']

def find_sub_dirs(path, depth=1):
    path = Path(path)
    assert path.exists(), f'Path: {path} does not exist'
    depth_search = '*/' * depth + '*.md'
    search_pattern = os.path.join(path, depth_search)
    return list(glob(f'{search_pattern}'))

def find_file_depth(file,args):
    for i in range (0,10):
        directories=find_sub_dirs(f'{args.dir}/content/',i)
        if len(directories) > 0:
                if file in directories and args.root:
                    return (i+1)
                elif file in directories:
                    return (i)

def add_numbering(files, args):
    """Adds frontmatter to markdown files in specified directory

    Arguments:
        files {list} -- The path to the markdown file/s to be processed
        args -- List of runtime arguments
    """
    numbering = []
    s_files=sorted(files, key=str.lower)
    for file in s_files:
        depth = find_file_depth(file,args)
        fm = frontmatter.load(file)
        ctitle = fm['title']
        if not file.endswith('_index.md'):
            depth = depth + 1
        if not depth == 0:
            title_list.append(f'{depth} {ctitle}±{file}')
    for item in title_list:
        num, _, text = item.partition(" ")
        text, _,file = text.partition("±")
        if int(num) == len(numbering):
            numbering[-1] += 1
        elif int(num) > len(numbering):
            numbering.extend([1] * (int(num) - len(numbering)))
        elif int(num) < len(numbering):
            numbering = numbering[:int(num)]
            numbering[-1] += 1
        num_title = (".".join(map(str, numbering)) + ". " + text)
        num_title_list.append(num_title + '±' + file)
    return(num_title_list)


def populate_title(file):
    for title in num_title_list:
        num_title, _, file_tracking = title.partition("±")
        if file_tracking == file:
            return num_title
    return ''

def add_frontmatter(files, args):
    """Adds frontmatter to markdown files in specified directory

    Arguments:
        files {list} -- The path to the markdown file/s to be processed
        args -- List of runtime arguments
    """
    template_str = ''.join(open(os.path.abspath(os.path.dirname(__file__) + "/template.j2"), "r").readlines())
    for file in files:
        bakfilename = os.path.basename(file) + '.bak'
        bakfile = os.path.join(os.path.dirname(file), bakfilename)
        path = Path(file)
        if file.endswith('_index.md') and not os.path.dirname(file).endswith('content'):
            path = Path(file)
            parentpath = os.path.join(path.parents[1], "_index.md")             
            if not os.path.dirname(parentpath).endswith('content'):
                if not os.path.exists(bakfile) and not args.nobackup:
                    shutil.copyfile(file,bakfile)
                pfm = frontmatter.load(parentpath)
                cfm = frontmatter.load(file)
                if args.number:
                    num_ctitle = populate_title(file)
                    cfm['title'] = num_ctitle
                    num_ptitle = populate_title(parentpath)
                    pfm['title']= num_ptitle
                proc = EditFrontMatter(file_path=file, template_str=template_str)
                proc.run({'title': cfm['title'],'parent': pfm['title'] })
                log.info(f'Writing frontmatter for {file}')
                proc.writeFile(file)
            else:
                if not os.path.exists(bakfile) and not args.nobackup:
                    shutil.copyfile(file,bakfile)
                cfm = frontmatter.load(file)
                if args.number:
                    num_ctitle = populate_title(file)
                    cfm['title'] = num_ctitle
                proc = EditFrontMatter(file_path=file, template_str=template_str)
                if args.root:
                    pfm = frontmatter.load(parentpath)
                    if args.number:
                        num_ptitle = populate_title(parentpath)
                        pfm['title']= num_ptitle
                    proc.run({'title': cfm['title'],'parent': pfm['title'] })
                    log.info(f'Writing frontmatter for {file}')
                    proc.writeFile(file)
                else:
                    proc.run({'title': cfm['title'] })
                    log.info(f'Writing frontmatter for {file}')
                    proc.writeFile(file)
        elif not file.endswith('_index.md'):
            if not os.path.exists(bakfile) and not args.nobackup:
                shutil.copyfile(file,bakfile)
            path = Path(file)
            parentpath = os.path.join(path.parents[0], "_index.md")
            pfm = frontmatter.load(parentpath)
            cfm = frontmatter.load(file)
            if args.number:
                num_ctitle = populate_title(file)
                cfm['title'] = num_ctitle
                num_ptitle = populate_title(parentpath)
                pfm['title']= num_ptitle
            proc = EditFrontMatter(file_path=file, template_str=template_str)
            proc.run({'title': cfm['title'],'parent': pfm['title'] })
            log.info(f'Writing frontmatter for {file}')
            proc.writeFile(file)
        elif file.endswith('_index.md') and os.path.dirname(file).endswith('content'):
            if not os.path.exists(bakfile) and not args.nobackup:
                shutil.copyfile(file,bakfile)
            cfm = frontmatter.load(file)
            if args.root:
                if args.number:
                    num_ctitle = populate_title(file)
                    cfm['title'] = num_ctitle
            proc = EditFrontMatter(file_path=file, template_str=template_str)
            proc.run({'title': cfm['title'] })
            log.info(f'Writing frontmatter for {file}')
            proc.writeFile(file)
    log.info(f'Write complete for {len(files)} files')

def parse_args():
    # Parse command line arguments
    
    parser = argparse.ArgumentParser(
        description='Adds required frontmatter to markdown page/s so they can be synced using markdown-to-confluence')
    parser.add_argument(
        '--dir',
        dest='dir',
        default='None',
        help='The path to your directory containing markdown pages (default: None)'
    )
    parser.add_argument(
        '--root',
        dest='root',
        action='store_true',
        help='Sets all base pages parent to be the root page'
    )
    parser.add_argument(
        '--nobackup',
        dest='nobackup',
        action='store_true',
        help='Does not create backups of all modified files'
    )
    parser.add_argument(
        '--number',
        dest='number',
        action='store_true',
        help='Adds numbering to the titles in the frontmatter'
    )
    parser.add_argument(
        '--force',
        dest='force',
        action='store_true',
        help='Forces overwrite of the frontmatter if it already exists'
    )
    parser.add_argument(
        '--diff',
        dest='diff',
        action='store_true',
        help='Forces overwrite of the frontmatter from a matching diff file in same directory'
    )
    parser.add_argument(
        '--dryrun',
        dest='dryrun',
        action='store_true',
        help='Prints changes that would be made to files without modifying them'
    )
    parser.add_argument(
        'posts',
        type=str,
        nargs='*',
        help=
        'Individual pages to add frontmatter to'
    )
    
    args = parser.parse_args()

    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    return parser.parse_args()

     
def main():
    args = parse_args()

    if args.posts:
        changed_posts = [os.path.abspath(post) for post in args.posts]
        for post_path in changed_posts:
            if not os.path.exists(post_path) or not os.path.isfile(post_path):
                log.error('File doesn\'t exist: {}'.format(post_path))
                sys.exit(1)
 
    elif args.dir != 'None':
          log.info(f'Checking content pages in directory {args.dir}')
          changed_posts = [
              os.path.join(path, name) for path, subdirs, files in os.walk(args.dir) for name in files
          ]
          for filepath in changed_posts[:]:
            _,ext = os.path.splitext(f'{filepath}')
            if ext not in SUPPORTED_FORMATS:
                changed_posts.remove(f'{filepath}')
            elif not filepath.startswith(f'{args.dir}/content/'):
                changed_posts.remove(f'{filepath}')

    else:
        log.info('No pages found in input source')
        return

    if not args.force:
        for p in changed_posts[:]:
            fm = frontmatter.load(p)
            try:
                test = fm['wiki']
            except:
                log.info(f'{p} set to be processed as it contains no Wiki frontmatter')
            else:
                changed_posts.remove(p)    

    if args.number:
        add_numbering(changed_posts,args)
    add_frontmatter(changed_posts, args)
  
    if args.diff:  
        diff_posts = [
              os.path.join(path, name) for path, subdirs, files in os.walk(args.dir) for name in files
          ]
        log.info('\n\n')
        log.info('Processing any existing diff files ........')        
        for filepath in diff_posts[:]:
            _,ext = os.path.splitext(f'{filepath}')     
            if ext not in DIFF_FILES or not filepath.startswith(f'{args.dir}/content/'):
                diff_posts.remove(f'{filepath}')
        for filepath in diff_posts[:]:
            file,ext = os.path.splitext(f'{filepath}')
            if file in changed_posts:
                template_str = ''.join(open(os.path.abspath(os.path.dirname(__file__) + "/template-diff.j2"), "r").readlines())
                difffm = frontmatter.load(filepath)
                origfm = frontmatter.load(file)
                try:
                    test = difffm['wiki']
                except:
                    log.info(f'{filepath} No Wiki frontmatter in diff file. Ignoring.')
                else:
                    if difffm['wiki'].get('title') == None:
                        log.info(f'{filepath} - No Wiki title frontmatter tag in diff file. Ignoring.')
                    else:
                        origfm['wiki']['title'] = difffm['wiki'].get('title')
                    
                    if difffm['wiki'].get('parent') == None:
                        log.info(f'{filepath} - No Wiki parent frontmatter tag in diff file. Ignoring.')
                    else:
                        origfm['wiki']['parent'] = difffm['wiki'].get('parent')
                    
                    if difffm['wiki'].get('share') == None:
                        log.info(f'{filepath} - No Wiki share frontmatter tag in diff file. Ignoring.')
                    else:
                        origfm['wiki']['share'] = difffm['wiki'].get('share')
                    
                    proc = EditFrontMatter(file_path=file, template_str=template_str)
                    proc.run({'share': (str(origfm['wiki'].get('share')).lower()),'title': origfm['wiki'].get('title'),'parent': origfm['wiki'].get('parent')})
                    log.info(f'Writing diff frontmatter from {filepath} to {file}')
                    proc.writeFile(file)
        log.info(f'Diff processing complete for {len(diff_posts)} diff files')

    seen = set()
    for p in changed_posts[:]:
        fm = frontmatter.load(p)
        if fm['wiki'].get('title') not in seen:
            seen.add(fm['wiki'].get('title'))
        else:
            skippedpages.append('"' + fm['wiki'].get('title') + '"' + ' at ' + p)

            
    if len(skippedpages) > 0:
        log.info('\n\n')
        log.info('---------- WARNING -----------')
        log.info('Confluence does not allow the creation of pages with the same title within the same Confluence Space.')
        log.info(f'{len(skippedpages)} pages could cause errors due to duplicate page titles. Please check the pages listed below for duplicate titles:\n')
        for s in skippedpages:
            log.info(s)
        log.info('--------------------------------------')
    
if __name__ == '__main__':
    main()
