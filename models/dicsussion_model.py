from extensions import db

class DiscussionModel(db.Model):
    __tablename__ = 'sc3_discussion_model'

    vote_id = db.Column(db.Integer, db.ForeignKey('sc3_vote_model.hash_id'), primary_key=True)

    vote = db.relationship('VoteModel', back_populates='discussion')
    comments = db.relationship('CommentModel', back_populates='discussion', lazy='dynamic')

    def __init__(self, **kwargs):
        super(DiscussionModel, self).__init__(**kwargs)

    @classmethod
    def default_discussion(cls, vote):
        return cls(vote=vote)

    def to_dict(self):
        return {
            "vote_id": self.vote_id,
            "comments": [comment.to_dict() for comment in self.comments]
        }