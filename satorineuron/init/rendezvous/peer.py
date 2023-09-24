import json
import time
from satorilib.concepts import StreamId
from satorirendezvous.example.client.structs.protocol import ToServerSubscribeProtocol
from satorirendezvous.example.client.connect import RendezvousAuthenticatedConnection
from satorirendezvous.example.peer.peer import SubscribingPeer
from satorineuron.init.rendezvous.topic import Topic, Topics


class AuthenticatedSubscribingPeer(SubscribingPeer):
    ''' manages connection to the rendezvous server and all our udp topics '''

    def __init__(
        self,
        streamIds: list[StreamId],
        rendezvousHost: str,
        rendezvousPort: int,
        signature: str = None,
        key: str = None,
        handlePeriodicCheckin: bool = True,
        periodicCheckinSeconds: int = 60*60*1,
    ):
        self.signature = signature
        self.key = key
        self.streamIds = streamIds
        super().__init__(
            rendezvousHost=rendezvousHost,
            rendezvousPort=rendezvousPort,
            topics=[streamId.topic() for streamId in streamIds],
            handlePeriodicCheckin=handlePeriodicCheckin,
            periodicCheckinSeconds=periodicCheckinSeconds)

    # override
    def createTopics(self, topics: list[str]):
        self.topics: Topics = Topics({k: Topic(k) for k in topics})

    def topicFor(self, streamId: StreamId):
        for name, topic in self.topics.items():
            if name == streamId.topic():
                return topic
        return None

    # override

    def connect(self, rendezvousHost: str, rendezvousPort: int):
        self.rendezvous: RendezvousAuthenticatedConnection = RendezvousAuthenticatedConnection(
            signature=self.signature,
            key=self.key,
            host=rendezvousHost,
            port=rendezvousPort,
            onMessage=self.handleRendezvousMessage)

    # never called
    def sendTopics(self):
        ''' send our topics to the rendezvous server to get peer lists '''
        for topic in self.topics.keys():
            self.sendTopic(topic)

    def sendTopic(self, topic: str):
        self.rendezvous.send(
            cmd=ToServerSubscribeProtocol.subscribePrefix,
            msgs=[
                "signature doesn't matter during testing",
                json.dumps({
                    **{'pubkey': 'wallet.pubkey'},
                    # **(
                    #    {
                    #        'publisher': [topic]}
                    # ),
                    **(
                        {
                            'subscriptions': [topic]
                        }
                    )})])
