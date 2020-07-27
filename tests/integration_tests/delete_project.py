import sys
import argparse
import flywheel

fw = flywheel.Client()
def delete_subjects(proj_id):
    for session in fw.get_project_subjects(proj_id):
        fw.delete_subject(session.id)


def main(args):
    project = fw.lookup(f'{args.group}/{args.project}')

    print(f'Deleting project {project.label}, confirm (y/N): ')
    confirm = input()

    if confirm and confirm == 'y':
        delete_subjects(project.id)
        if not args.data_only:
            fw.delete_project(project.id)
    else:
        print('exiting')
        sys.exit(0)




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Delete a Dummy Project')
    parser.add_argument('--group', help='Group')
    parser.add_argument('--project', help='Project')
    parser.add_argument('--data-only',help='Only delete project data, not project container',
                        action='store_true')

    args = parser.parse_args()
    main(args)
