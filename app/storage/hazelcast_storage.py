import hazelcast


class HZStorage:
    def __init__(self):
        self.client = hazelcast.HazelcastClient(
            cluster_name="dev",
            cluster_members=[
                "127.0.0.1:5701",
                "127.0.0.1:5702",
                "127.0.0.1:5703",
            ],
        )
        self.atomic = self.client.cp_subsystem.get_atomic_long("counter")

    async def read(self) -> int:
        return self.atomic.get().result()

    async def increment(self) -> int:
        return self.atomic.increment_and_get().result()
