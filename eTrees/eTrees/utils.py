
from account.models import Trainer
from createstory.models import Project

def returnAdmin(user):
	checkTrainer = Trainer.objects.filter(user__id = user.id)
	if len(checkTrainer) > 0:
		return checkTrainer[0].admin
	return user