import Player
import QueueManager
import queue
from database import MusicDatabase
import ExplorationManager
from time import sleep


class MusicWizard:
    def __init__(self, feedback_receiver, user_name='remi'):
        self.user_name = user_name
        self.feedback_receiver = feedback_receiver

        self.music_database = MusicDatabase.MusicDatabase()
        self.music_database.create()

        self.score_update_queue = queue.Queue()
        self.exploration_manager = ExplorationManager.ExplorationManager(self.user_name, self.score_update_queue)
        self.exploration_manager.daemon = True

        print("[MUSIC WIZARD] explorer initialized")

        self.song_queue = queue.Queue()  # the queue used for receiving information from the song_chooser thread

        self.player = Player.Player(self.song_queue, self.music_database,
                                    self.score_update_queue)  # initialize the music player
        self.sleep_time = 0.5

        self.queue_manager = QueueManager.QueueManager(self.song_queue, self.music_database, self.player,
                                                       self.user_name,
                                                       self.score_update_queue)  # creating a thread that will work in parallel
        self.queue_manager.daemon = True  # when the main is closed this thread will also close

        print("[MUSIC WIZARD] vlc player initialized")

        self.feedback_receiver.initialize(self)

        self.queue_manager.start()
        self.exploration_manager.start()

    def run(self):
        self.player.play_next_music(0)
        # player.pause()

        print("[MUSIC WIZARD] starting to play")

        while True:
            if self.player.music_ended():
                self.player.play_next_music(0.1)

            if self.feedback_receiver.need_to_stop_main:
                self.close()
                break

            sleep(self.sleep_time)
            continue
        
    def close(self):
        self.queue_manager.stop = True
        self.exploration_manager.stop = True
        print("[MUSIC WIZARD] session closed")
        sleep(1)
