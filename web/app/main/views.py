"""
The main public routes to view the site
"""

from flask import render_template, current_app

from .blueprint import main
from app.database import gage_sample
from ..models import Gage, Region, Section, River, Sensor

# Normal Pages


@main.route('/')
def indexpage():
    """**/**

    Index page
    """
    return render_template('index.html', gage_sample=gage_sample)


@main.route('/about/')
def aboutpage():
    """**/about/**

    About this site.
    """
    return render_template('about.html', gage_sample=gage_sample)


@main.route('/map/')
def mappage():
    """**/map/**

    Map of gages and sections
    """
    mapbox_access_token = current_app.config['MAPBOX_ACCESS_TOKEN']
    return render_template('map.html',
                           gage_sample=gage_sample,
                           Gage=Gage,
                           Section=Section,
                           mapbox_access_token=mapbox_access_token)


@main.route('/gages/')
@main.route('/gage/')
def gagespage():
    """**/gages/**

    List of gages currently not grouped by regions,
    or anything else for that matter.
    """
    return render_template('gages.html', Gage=Gage)


@main.route('/gage/<int:gid>/')
@main.route('/gage/<slug>/')
def gagepage(gid=None, slug=None):
    """**/gage/<slug>/**

    Individual gage page
    """
    if slug is None:
        gage = Gage.query.get_or_404(gid)
    else:
        gage = Gage.query.filter_by(slug=slug).first_or_404()
    return render_template('gage.html', Gage=Gage, gage=gage, gage_sample=gage_sample)


@main.route('/regions/')
@main.route('/region/')
def regionspage():
    """**/regions/**

    List all regions
    """
    return render_template('regions.html', Gage=Gage, Region=Region)


@main.route('/region/<int:rid>/')
@main.route('/region/<slug>/')
def regionpage(rid=None, slug=None):
    """**/region/<slug>/**

    Individual region page
    """
    if slug is None:
        region = Region.query.get_or_404(rid)
    else:
        region = Region.query.filter_by(slug=slug).first_or_404()
    return render_template('region.html',
                           Gage=Gage,
                           Region=Region,
                           region=region,
                           Section=Section,
                           River=River,
                           gage_sample=gage_sample)


@main.route('/sections/')
@main.route('/section/')
def sectionspage():
    """**/sections/**

    List all sections
    """
    return render_template('sections.html', Gage=Gage, Section=Section)


@main.route('/section/<int:sid>/')
@main.route('/river/<river>/<slug>/')
def sectionpage(sid=None, slug=None, river=None):
    """**/section/<slug>/**

    Individual section page
    """
    if river and slug:
        section = Section.query.join(Section.river)\
                               .filter(River.slug == river)\
                               .filter(Section.slug == slug)\
                               .first_or_404()
    else:
        section = Section.query.get_or_404(sid)
    return render_template('section.html',
                           Gage=Gage,
                           Section=Section,
                           section=section,
                           Sensor=Sensor,
                           gage_sample=gage_sample)


@main.route('/rivers/')
@main.route('/river/')
def riverspage():
    """**/rivers/**

    List all rivers
    """
    return render_template('rivers.html',
                           Gage=Gage,
                           River=River,
                           Section=Section)


@main.route('/river/<int:rid>/')
@main.route('/river/<slug>/')
def riverpage(rid=None, slug=None):
    """**/river/<slug>/**

    Individual river page
    """
    if slug is None:
        river = River.query.get_or_404(rid)
    else:
        river = River.query.filter_by(slug=slug).first_or_404()
    return render_template('river.html',
                           Gage=Gage,
                           River=River,
                           Section=Section,
                           river=river,
                           gage_sample=gage_sample)
