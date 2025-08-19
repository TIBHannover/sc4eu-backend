from extensions import db
from ._base import ModelMixin

class CommentModel(db.Model, ModelMixin):
    __tablename__ = 'sc3_comment_model'

    id = db.Column('hash_id', db.Integer, primary_key=True, unique=True)
    discussion_id = db.Column(db.Integer, db.ForeignKey('sc3_discussion_model.vote_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('sc3_user_model.hash_id'))
    text = db.Column(db.String, nullable=False)

    discussion = db.relationship('DiscussionModel', back_populates='comments')
    user = db.relationship('UserModel', back_populates='comments')

    @classmethod
    def create_new_comment(cls, discussion, user, text):
        new_entry = CommentModel()
        new_entry.discussion = discussion
        new_entry.user = user
        new_entry.text = text
        return new_entry

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "user_id": self.user_id,
        }