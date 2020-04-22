"""
init_db.py
Populates database with initial values
"""

from models import Category, ContentTag, Post, DemogTag, User

def init_db(db):

    # Create models
    db.drop_all()
    db.create_all()

    additions = []

    # Establish categories and content tags
    cat_tags = {
        'Transition to College': ['Adjusting to Campus',
                                  'Making Friends',
                                  'Joining Extracurriculars',
                                  'Professors',
                                  'Choosing a Major',
                                  'Working as a Student'],
        'Pursuing Graduate Studies': ['Masters Programs',
                                      'Doctoral Programs',
                                      'Law School',
                                      'Business School',
                                      'Medical School'],
        'Navigating Careers': ['Arts',
                               'Business',
                               'Data',
                               'Design',
                               'Engineering',
                               'Entrepreneurship',
                               'Finance',
                               'Journalism',
                               'Law',
                               'Marketing',
                               'Medicine',
                               'Nonprofit',
                               'Product',
                               'Research',
                               'Software/Tech']
    }
    for category, tags in cat_tags.items():
        category_add = Category(label=category)
        additions.append(category_add)
        for tag in tags:
            ContentTag(label=tag, category=category_add)

    # Establish demographic tags
    demog_tags = ['Man', 'Woman', 'Non-Binary', 'LGBTQIA+', 'Transgender', 'Asian', 'Black', 'Latinx', 'Middle Eastern',
                  'Native', 'Pacific Islander', 'White', 'First-Generation Student', 'International Student', 'Immigrant']
    for tag in demog_tags:
        additions.append(DemogTag(label=tag))

    # Add everything
    for model in additions:
        db.session.add(model)

    # Populate example post
    db.session.add(
        Post(
            author=User(name_first='Cat',
                        email='xaliceli@gmail.com',
                        dtags=[db.session.query(DemogTag).filter(DemogTag.label == 'Woman').first(),
                               db.session.query(DemogTag).filter(DemogTag.label == 'Asian').first(),
                               db.session.query(DemogTag).filter(DemogTag.label == 'First-Generation Student').first()]),
            category=db.session.query(Category).filter(Category.label == 'Navigating Careers').first(),
            ctags=[db.session.query(ContentTag).filter(ContentTag.label == 'Software/Tech').first()],
            q_name='Cat',
            q_about='I have been working as a cat wrangler for three years, most recently as a Senior Cat Wrangling Engineer at Kedi & Associates. I entered the cat wrangling field as a Cat Wrangling Intern at Garfield Co. I am most proud of my accomplishments implementing a catnap service that improved customer satisfaction by 50%.',
            q_interest='I grew up on a farm with twelve cats and have always been interested in improving the experience of felines. In college I majored in Cat Studies and became very interested in cat wrangling specifically due to its combination of quantitative rigor and creative, out-of-the-box thinking. I loved my internship at Garfield Co. and took a full-time offer there at the end of my internship summer.',
            q_challenges="I was excited but really, really nervous. Cat wrangling is a competitive field and I didn't go to one of the famous target schools. The first month of my internship was really stressful because there were a lot of technologies that I'd never been exposed to. All of the other interns seemed so familiar with all of these complicated tools like HairBall and Treetz. To be honest I worried for a while that I wasn't cut out for cat wrangling at all. The turning point was when I confided in my mentor at work about how I felt. They told me that I wasn't expected to know everything right away, that they also felt like I did when they were an intern, and that I was doing a good job learning and observing. We set realistic goals for my summer together, and I actually made suggestions for how future interns could be better trained and onboarded that Garfield Co. is still using today.",
            q_change="Junior cat wranglers tend to be generalists while senior cat wranglers tend to specialize. I had initially thought that I was much better suited for the project management side of cat wrangling. It turns out that, while management felt glamorous to me in college, I found all of the frequent meetings surprisingly draining and relished the moments where I could sit down and think at my own pace. I'd shied away from the quantitative work at first and never thought of myself as good at math because so many students in undergrad seemed much more knowledgeable, but came to discover that I quite enjoyed it and was good at applying mathematical models to cat behavior. These days I spend most of my time building advanced cat motion models, which I would've never expected but find so fulfilling!",
            q_helpful="The National Association of Cat Wranglers sponsors a number of scholarships to their annual conference for undergrads interested in the field, including specific funds dedicated to supporting underrepresented minorities. The scholarship pays all travel, lodging, and conference expenses and offers tremendous opportunities to meet one-on-one with leaders in the field. Candidates aren't expected to have prior experience in cat wrangling unlike a lot of other internships and opportunities, so this was huge for me. I did not see myself as an amazing student or rising star, especially since I barely knew anything about cat wrangling at the time. I felt really fortunate to have received the scholarship and probably wouldn't have landed my first internship otherwise.",
            q_other="I love this field and would encourage anyone who is interested in creative, multi-disciplinary projects to learn more and see if this is a good fit for you!"
        )
    )

    db.session.commit()
