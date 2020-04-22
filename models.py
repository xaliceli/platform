"""
models.py
Defines database model schema.
"""
from flask_bcrypt import Bcrypt
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_login import LoginManager, UserMixin
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.hybrid import hybrid_property

from init_app import db, app

bcrypt = Bcrypt()
bcrypt.init_app(app)

# =====================================================
# ASSOCIATION TABLES
# For many to many relationships
# =====================================================

# Users to demographic tags
assoc_user_dtag = db.Table('assoc_user_dtag', db.Model.metadata,
                           db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                           db.Column('dtag_id', db.Integer, db.ForeignKey('demog_tag.id'))
                           )

# Users to positions
assoc_user_pos = db.Table('assoc_user_pos', db.Model.metadata,
                          db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                          db.Column('pos_id', db.Integer, db.ForeignKey('position.id'))
                          )

# Posts to positions
assoc_post_pos = db.Table('assoc_post_pos', db.Model.metadata,
                          db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
                          db.Column('pos_id', db.Integer, db.ForeignKey('position.id'))
                          )

# Users to category subscription
assoc_user_category = db.Table('assoc_user_category', db.Model.metadata,
                               db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                               db.Column('cat_id', db.Integer, db.ForeignKey('category.id'))
                               )

# Users to content tag subscription
assoc_user_ctag = db.Table('assoc_user_ctag', db.Model.metadata,
                           db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                           db.Column('ctag_id', db.Integer, db.ForeignKey('content_tag.id'))
                           )

# Posts to content tags
assoc_post_ctag = db.Table('assoc_post_ctag', db.Model.metadata,
                           db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
                           db.Column('ctag_id', db.Integer, db.ForeignKey('content_tag.id'))
                           )

# Posts to reactions
assoc_post_reaction = db.Table('assoc_post_reaction', db.Model.metadata,
                               db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
                               db.Column('react_id', db.Integer, db.ForeignKey('reaction.id'))
                               )

# Users to saved posts
assoc_post_save = db.Table('assoc_post_save', db.Model.metadata,
                           db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
                           db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
                           )


# =====================================================
# USER TABLES
# =====================================================

class User(UserMixin, db.Model):
    __tablename__ = 'user'

    # Basic information
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.LargeBinary, nullable=True)
    name_first = db.Column(db.String)
    name_mid = db.Column(db.String)
    name_last = db.Column(db.String)
    reg_date = db.Column(db.TIMESTAMP)

    # Bidirectional many-to-many demog tag <-> user relationship
    dtags = db.relationship('DemogTag',
                            secondary=assoc_user_dtag,
                            back_populates='users')

    # Bidirectional many-to-many user <-> position
    positions = db.relationship('Position',
                                secondary=assoc_user_pos,
                                back_populates='users')

    # Bidirectional one-to-many author <-> post relationship
    posts_authored = db.relationship('Post', back_populates='author')

    # Bidirectional many-to-many user <-> saved posts relationship
    saves = db.relationship('Post',
                            secondary=assoc_post_save,
                            back_populates='savers')

    # Bidirectional one-to-many user <-> reaction relationship
    reactions = db.relationship('Reaction', back_populates='user')

    # Bidirectional many-to-many user <-> category to subscription relationship
    sub_categories = db.relationship('Category',
                                     secondary=assoc_user_category,
                                     back_populates='subscribers')

    # Bidirectional many-to-many user <-> category to subscription relationship
    sub_ctags = db.relationship('ContentTag',
                                secondary=assoc_user_ctag,
                                back_populates='subscribers')

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password)

    @password.deleter
    def password(self):
        self.password_hash = None

    @property
    def has_password(self):
        return bool(self.password_hash)

    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def react_post(self, reaction, post_id):
        if not self.reacted_post(reaction, post_id):
            reaction = Reaction(user_id=self.id, post_id=post_id, label=reaction)
            db.session.add(reaction)
        else:
            Reaction.query.filter_by(
                user_id=self.id,
                post_id=post_id,
                label=reaction).delete()

    def reacted_post(self, reaction, post_id):
        return Reaction.query.filter(
            Reaction.user_id == self.id,
            Reaction.post_id == post_id,
            Reaction.label == reaction).count() > 0


class DemogTag(db.Model):
    __tablename__ = 'demog_tag'

    # Basic information
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String)

    # Bidirectional many-to-many demog tag <-> user relationship
    users = db.relationship('User',
                            secondary=assoc_user_dtag,
                            back_populates='dtags')


class Position(db.Model):
    __tablename__ = 'position'

    # Basic information
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    industry = db.Column(db.String)
    org = db.Column(db.String)

    # Bidirectional many-to-many user <-> position
    users = db.relationship('User',
                            secondary=assoc_user_pos,
                            back_populates='positions')

    # Bidirectional many-to-many post <-> position
    posts = db.relationship('Post',
                            secondary=assoc_post_pos,
                            back_populates='positions')


# =====================================================
# CONTENT TABLES
# =====================================================

class Category(db.Model):
    __tablename__ = 'category'

    # Basic information
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String)

    # Bidirectional one-to-many category <-> content tag relationship
    ctags = db.relationship('ContentTag', back_populates='category')

    # Bidirectional one-to-many category <-> post relationship
    posts = db.relationship('Post', back_populates='category')

    # Bidirectional many-to-many user <-> category to subscription relationship
    subscribers = db.relationship('User',
                                  secondary=assoc_user_category,
                                  back_populates='sub_categories')


class ContentTag(db.Model):
    __tablename__ = 'content_tag'

    # Basic information
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String)

    # Bidirectional one-to-many category <-> content tag relationship
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', back_populates='ctags')

    # Bidirectional many-to-many content tag <-> post relationship
    posts = db.relationship('Post',
                            secondary=assoc_post_ctag,
                            back_populates='ctags')

    # Bidirectional many-to-many user <-> category to subscription relationship
    subscribers = db.relationship('User',
                                  secondary=assoc_user_ctag,
                                  back_populates='sub_ctags')


class Reaction(db.Model):
    __tablename__ = 'reaction'

    # Basic information
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String)
    time = db.Column(db.TIMESTAMP, default=db.func.now())

    # Bidirectional one-to-many user <-> reaction relationship
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='reactions')

    # Bidirectional one-to-many post <-> reaction relationship
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    posts = db.relationship('Post', back_populates='reactions')


class Post(db.Model):
    __tablename__ = 'post'

    # Basic information
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.TIMESTAMP, default=db.func.now())

    # Bidirectional one-to-many author <-> post relationship
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', back_populates='posts_authored')

    # Bidirectional one-to-many category <-> post relationship
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', back_populates='posts')

    # Bidirectional many-to-many content tag <-> post relationship
    ctags = db.relationship('ContentTag',
                            secondary=assoc_post_ctag,
                            back_populates='posts')

    # Bidirectional one-to-many post <-> reactions relationship
    reactions = db.relationship('Reaction', back_populates='posts')

    # Bidirectional many-to-many user <-> saved posts relationship
    savers = db.relationship('User',
                             secondary=assoc_post_save,
                             back_populates='saves')

    # Bidirectional many-to-many post <-> position
    positions = db.relationship('Position',
                                secondary=assoc_post_pos,
                                back_populates='posts')

    # Content
    q_name = db.Column(db.Text)
    q_about = db.Column(db.Text)
    q_interest = db.Column(db.Text)
    q_challenges = db.Column(db.Text)
    q_change = db.Column(db.Text)
    q_helpful = db.Column(db.Text)
    q_other = db.Column(db.Text)

    def dict(self):
        return {
            'time': self.time,
            'author': self.author,
            'category': self.category,
            'ctags': self.ctags,
            'reactions': self.reactions,
            'q_name': self.q_name,
            'q_about': self.q_about,
            'q_interest': self.q_interest,
            'q_challenges': self.q_challenges,
            'q_change': self.q_change,
            'q_helpful': self.q_helpful,
            'q_other': self.q_other
        }

    def get_reactions(self):
        reactions = {}
        for reaction in ['Like', 'Dislike', 'Encouraging', 'Eye-Opening', 'Helpful', 'Motivating', 'Reassuring']:
            reactions[reaction] = Reaction.query.filter(Reaction.label == reaction.lower(),
                                                        Reaction.post_id == self.id).count()
        return reactions

    @hybrid_property
    def sort_overall(self):
        reactions = 0
        for reaction in ['Like', 'Encouraging', 'Eye-Opening', 'Helpful', 'Motivating', 'Reassuring']:
            reactions += Reaction.query.filter(Reaction.label == reaction.lower(),
                                               Reaction.post_id == self.id).count()
        reactions -= Reaction.query.filter(Reaction.label == 'dislike',
                                           Reaction.post_id == self.id).count()
        return reactions

    @hybrid_property
    def sort_like(self):
        return Reaction.query.filter(Reaction.label == 'like', Reaction.post_id == self.id).count()

    @hybrid_property
    def sort_encouraging(self):
        return Reaction.query.filter(Reaction.label == 'encouraging', Reaction.post_id == self.id).count()

    @hybrid_property
    def sort_eyeopening(self):
        return Reaction.query.filter(Reaction.label == 'eye-opening', Reaction.post_id == self.id).count()

    @hybrid_property
    def sort_helpful(self):
        return Reaction.query.filter(Reaction.label == 'helpful', Reaction.post_id == self.id).count()

    @hybrid_property
    def sort_motivating(self):
        return Reaction.query.filter(Reaction.label == 'motivating', Reaction.post_id == self.id).count()

    @hybrid_property
    def sort_reassuring(self):
        return Reaction.query.filter(Reaction.label == 'reassuring', Reaction.post_id == self.id).count()


# =====================================================
# OAUTH FUNCTIONALITY
# =====================================================

class OAuth(OAuthConsumerMixin, db.Model):
    __table_args__ = (db.UniqueConstraint("provider", "provider_user_id"),)
    provider_user_id = db.Column(db.String(256), nullable=False)
    provider_user_login = db.Column(db.String(256), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    user = db.relationship(
        User,
        # This `backref` thing sets up an `oauth` property on the User model,
        # which is a dictionary of OAuth models associated with that user,
        # where the dictionary key is the OAuth provider name.
        backref=db.backref(
            "oauth",
            collection_class=attribute_mapped_collection("provider"),
            cascade="all, delete-orphan",
        ),
    )


# setup login manager
login_manager = LoginManager()
login_manager.login_view = "auth.join"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

