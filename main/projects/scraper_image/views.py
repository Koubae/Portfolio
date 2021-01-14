from flask import render_template, Blueprint, request, redirect, url_for, send_file, flash 
from .scraper  import Downloader

scrap_proj = Blueprint('scrap_proj', __name__)

my_downloader = Downloader()

@scrap_proj.route('/scraper_images')
def scrap_index():
    return render_template('projects/scraper_images.html')

@scrap_proj.route('/scraper_images/demo', methods=['GET', 'POST'])
def scrap_download():

    data = None
    
    if request.method == 'POST':
        keywords = request.form['keywords']
        if not keywords:
            print('Client did not add Keyword, Redirect to index...')
            # flash('Please Enter a keyword')
            return redirect(url_for('index'))
        total = int(request.form['total'])
        try:
            data = my_downloader.download(keywords, limit=total)
        except Exception as err:
            print(err)
            return redirect(url_for('index'))

        if data:            
            return send_file(data,
                            mimetype='application/zip',
                            as_attachment=True,
                            attachment_filename='GoogleImages.zip')
        else:
            print('Error Occurred')
            return redirect(url_for('index'))
    else:
        print('Cant Post right now...')
        return redirect(url_for('index'))


    