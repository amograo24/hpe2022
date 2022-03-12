import json
from typing import Union

from django.http import HttpResponse, JsonResponse
from django.utils import timezone

from health_tracker.models import User, MedWorkerRep, Patients, Notification


class NotificationManager:
    notif_object = None
    sender_mwr = None
    receiver_p = None

    def handle_send(self) -> HttpResponse:
        if self.sender.division.lower() == "nou":
            return HttpResponse("You can't bro sorry")

        if self.sender.username != self.request.user.username:
            return HttpResponse("Can't Invite yourself")

        if self.sender.division.lower() == self.receiver.division.lower():
            return HttpResponse("Just Can't")

        if self.sender_mwr in self.receiver_p.hcw_v.all():
            return HttpResponse("User Already Approved!")

        if self.sender.division.lower() != self.request.user.division.lower():
            return HttpResponse("Not authorised")

        check_notif = Notification.objects.filter(sender=self.sender, receiver=self.receiver)

        if check_notif and check_notif[0] != "rejected":
            return HttpResponse("Notification Already Sent!")

        self.notif_object = Notification(sender=self.sender, receiver=self.receiver, content="send")
        self.notif_object.save()
        return HttpResponse("Notification Sent!")

    def handle_receive(self) -> Union[JsonResponse, HttpResponse]:
        if self.sender.division.lower() != self.request.user.division.lower():
            return HttpResponse("Not authorised")
        all_notifs = []
        if self.request.user.division.lower() != "nou":
            print(self.sender)
            notifs = Notification.objects.filter(receiver=self.sender).order_by('-date_of_approval')
        else:
            notifs = Notification.objects.filter(receiver=self.sender).order_by('-date_of_approval')

        for notification in notifs:
            serialized_data = {
                'content': notification.content,
                'sender': notification.sender.username,
                'receiver': notification.receiver.username,
                'doc': f"{notification.date_of_approval.date()}"
            }
            all_notifs.append(serialized_data)

        return JsonResponse(all_notifs, content_type="json", safe=False)

    def handle_approve(self):
        notif_obj = Notification.objects.get(sender=self.sender, receiver=self.receiver)
        if self.body["status"] == "yes":
            status = "approved"
            print(self.sender_mwr)
            self.receiver_p.hcw_v.add(self.sender_mwr)

        else:
            status = "rejected"

        new_notif = Notification(sender=self.receiver, receiver=self.sender, content=status)
        new_notif.save()

        notif_obj.content = status
        notif_obj.date_of_approval = timezone.now()
        self.receiver_p.save()
        self.sender_mwr.save()
        notif_obj.save()

        return HttpResponse("Validation done!")

    def __init__(self, request, sender: User, receiver: User = None):
        self.request = request
        self.body = json.loads(request.body)
        self.sender = sender
        self.receiver = receiver

        self.type = self.body['type']

    def validate_request(self):

        big_brain = self.request.user.username if not self.receiver else self.body['as']
        self.sender_mwr = MedWorkerRep.objects.filter(hcwvid=big_brain)
        if self.sender_mwr:
            self.sender_mwr = self.sender_mwr[0]

        if self.receiver:
            self.receiver_p = Patients.objects.get(wbid=self.receiver.username)

        return self.__fmap[self.type](self)

    __fmap = {
        "send": handle_send,
        "receive": handle_receive,
        "approval": handle_approve
    }

    def set_receiver(self, receiver: User):
        self.receiver = receiver
