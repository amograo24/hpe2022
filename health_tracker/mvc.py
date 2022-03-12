import json

from django.http import HttpResponse, JsonResponse
from django.utils import timezone

from health_tracker.models import User, MedWorkerRep, Patients, Notification


class NotificationManager:
    notif_object = None
    sender_mwr = None
    receiver_p = None

    def handle_send(self) -> HttpResponse:
        if self.sender_mwr in self.receiver_p.hcw_v.all():
            return HttpResponse("User Already Approved!")

        self.notif_object = Notification(sender=self.sender, receiver=self.receiver, content="send")
        self.notif_object.save()
        return HttpResponse("Notification Sent!")

    def handle_receive(self) -> JsonResponse:
        all_notifs = []
        if self.request.user.division != "nou":
            notifs = Notification.objects.filter(receiver=self.sender).order_by('-date_of_approval')
        else:
            notifs = Notification.objects.filter(receiver=self.receiver).order_by('-date_of_approval')

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

    def __init__(self, request, sender: User, receiver: User, type_: str):
        self.request = request
        self.body = json.loads(request.body)
        self.sender = sender
        self.receiver = receiver

        self.type = type_

    def validate_request(self):
        if self.sender.username != self.request.user.username:
            return HttpResponse("Can't Invite yourself")

        elif self.sender.division.lower() == "nou" or self.sender.division != self.request.user.division.lower():
            return HttpResponse("Not authorised")

        "Validating if sender exists"
        self.sender_mwr = MedWorkerRep.objects.filter(user=self.request.user)
        if self.sender_mwr:
            self.sender_mwr = self.sender_mwr[0]
        else:
            return HttpResponse("Sender not found!")

        "Validating if receiver Exists"
        self.receiver_p = Patients.objects.filter(wbid=self.receiver.username)
        if self.receiver_p:
            self.receiver_p = self.receiver_p[0]
        else:
            return HttpResponse("Receiver not found!")

        return self.__fmap[self.type]()

    __fmap = {
        "send": handle_send,
        "receive": handle_receive,
        "approve": handle_approve
    }