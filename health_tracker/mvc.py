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
        """
        Handles logic for sending a notification from a User instance to another User Instance
        """
        if self.sender.division.lower() == "nou":
            return HttpResponse("Access Denied")

        if self.sender.username != self.request.user.username:
            return HttpResponse("Cannot Self Invite")

        if self.receiver.division in ['D/HCW/MS', 'I/SP', 'MSh']:
            return HttpResponse("Cannot request another Medical worker")

        if self.sender_mwr in self.receiver_p.hcw_v.all():
            return HttpResponse("User Already Approved!")

        if self.sender.division.lower() != self.request.user.division.lower():
            return HttpResponse("Not authorised")

        check_notif = Notification.objects.filter(sender=self.sender, receiver=self.receiver).order_by('-date_of_approval')
        print(check_notif)
        if check_notif and check_notif[0].content not in ("rejected", "approved"):
            return HttpResponse("Notification Already Sent!")

        self.notif_object = Notification(sender=self.sender, receiver=self.receiver, content="send")
        self.notif_object.save()
        return HttpResponse(f"You sent an authorization request to {self.receiver_p.full_name} ({self.receiver.username})")

    def handle_receive(self) -> Union[JsonResponse, HttpResponse]:
        """
        Returns a JsonResponse of all the notifications a user is associated with.
        """
        if self.sender.division.lower() != self.request.user.division.lower():
            return HttpResponse("Not authorised")
        all_notifs = []
        if self.request.user.division.lower() != "nou":
            notifs = Notification.objects.filter(receiver=self.sender).order_by('-date_of_approval')
        else:
            notifs = Notification.objects.filter(receiver=self.sender).order_by('-date_of_approval')

        for notification in notifs:
            if self.sender.division.lower() != "nou":
                rec = Patients.objects.get(person=notification.sender).full_name
                sen = MedWorkerRep.objects.get(account=self.sender).full_com_name
            else:
                sen = MedWorkerRep.objects.get(account=notification.sender).full_com_name
                rec = Patients.objects.get(person=self.sender).full_name
            serialized_data = {
                'content': notification.content,
                'sender': notification.sender.username,
                'receiver': notification.receiver.username,
                'doc': f"{notification.date_of_approval.date()}",
                "sender_name": sen,
                "receiver_name": rec
            }
            all_notifs.append(serialized_data)

        return JsonResponse(all_notifs, content_type="json", safe=False)

    def handle_approve(self):
        """
        Handles logic for approving a notification from a User instance for another User Instance
        """
        notif_obj = Notification.objects.filter(sender=self.sender, receiver=self.receiver).order_by('-date_of_approval')[0]
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
        """
        request: WSGI Request Object.
        sender: User instance, A notification Object's sender. Can be a Patient or a MedWorker
        receiver: User instance, A notification Object's receiver. Can be a Patient or a MedWorker
        """
        self.request = request
        self.body = json.loads(request.body)
        self.sender = sender
        self.receiver = receiver

        self.type = self.body['type']

    def validate_request(self):
        """
        Validates the request sent to the notification API, and decides the logistics based on the
        type of the request.
        """
        # TODO kushurox: Test the usefulness of this line
        receiver_temp = self.request.user.username if not self.receiver else self.body['as']
        self.sender_mwr = MedWorkerRep.objects.filter(hcwvid=receiver_temp)
        if self.sender_mwr:
            self.sender_mwr = self.sender_mwr[0]

        if self.receiver:
            self.receiver_p = Patients.objects.get(wbid=self.receiver.username)

        return self.__fmap[self.type](self)

    # Function map for calling the method based on the type of the request
    __fmap = {
        "send": handle_send,
        "receive": handle_receive,
        "approval": handle_approve
    }

    def set_receiver(self, receiver: User):
        """
        receiver: User instance
        Sets the receiver of the class instance
        """
        self.receiver = receiver


class StateManager:
    def __init__(self, states: dict):
        """
        states: dictionary of all the states and its respective districts
        """
        self.states = states

    def get_districts(self, sn: str) -> list:
        """
        sn: state name
        return: Returns the respective districts of state in the form of a list
        """
        return list(self.states.get(sn)) or []

    def get_states(self) -> list:
        """
        return: Returns all the states in the form of a list
        """
        return list(self.states.keys())
