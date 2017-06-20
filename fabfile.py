import copy, os

from fabric.api import local, prompt
from fabric.contrib.console import confirm
import yaml
from git import Repo as _Repo


def _image_version(config):
    """
    Returns the image and version from a kubernets config
    """
    image_version = config['spec']['template']['spec']['containers'][0]['image']
    return image_version.split(':')  # image, version


def _build(image, version, directory):
    """
    Builds docker image from directory after confirmation
    """
    tag = image + ':' + str(version)
    if confirm('Build new version {v} of {i}?'.format(i=image, v=version)):
        print('')
        local('docker build -t {t} {d}'.format(t=tag, d=directory))


def  _push(image, version):
    """
    Pushes image to gcloud
    """
    tag = image + ':' + str(version)
    if confirm('Push image {t} to gcloud?'.format(t=tag)):
        print('')
        local('gcloud docker -- push {t}'.format(t=tag))


def _git_tag(version):
    """
    Tags the latest commit with the new version
    """
    if confirm('Tag latest commit to repo?'):
        repo = _Repo(os.path.dirname(os.path.abspath(__file__)))
        commit = repo.head.commit
        repo.create_tag(version, ref=commit)


def _update_config_image(config, tag):
    """
    Returns a new config object with updated image tag
    """
    config['spec']['template']['spec']['containers'][0]['image'] = tag
    return config


def _update_config(filename, tag):
    """
    Updates the config file for latest tag
    """
    with open(filename) as f:
        config = yaml.safe_load(f)
    
    new_config = _update_config_image(copy.deepcopy(config), tag)
    yaml_config = yaml.dump(new_config, default_flow_style=False)

    print('New config:')
    print('')
    print(yaml_config)
    print('')

    if confirm('Write config to file?'):
        with open(filename, 'w') as f:
            f.write(yaml_config)


def _k8s_replace(filename):
    """
    Kubectl replace given filename
    """
    if confirm('Replace ' + filename + ' in k8s?'):
        local('kubectl replace -f ' + filename)


def deploy():
    """
    Deploy updated web, celery, and celery-beat containers to kubernetes
    """

    paths = ('k8s/web.yaml', 'k8s/celery.yaml', 'k8s/celery-beat.yaml')

    with open(paths[0]) as f:
        config = yaml.safe_load(f)
        image, version = _image_version(config)
    
    print('Current version {v} for image {i}'.format(v=version, i=image))

    new_version = prompt('New version:')
    print('')

    _build(image, new_version, 'web/')
    print('')

    _push(image, new_version)
    print('')

    tag = image + ':' + str(new_version)

    for path in paths:
        _update_config(path, tag)
        _k8s_replace(path)


    # git tag, push
    # sentry release tracking?
    # for path in paths:
        # write new config
        # replace

    # copy static files to nginx pod and push