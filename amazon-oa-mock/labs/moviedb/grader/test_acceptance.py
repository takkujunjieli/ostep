from django.contrib.auth.models import User
from django.test import TestCase
from app.models import Actor, Follow, Movie, Notification
from app.notifications import notify_followers


class Acceptance(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user("alice")
        self.bob = User.objects.create_user("bob")
        self.admin = User.objects.create_user("admin", is_staff=True)
        self.actor = Actor.objects.create(name="Maya")
        self.actor2 = Actor.objects.create(name="Alex")
        self.client.force_login(self.alice)

    def post(self, path, data=None):
        return self.client.post(path, data or {}, content_type="application/json")

    def test_01_follow_is_persisted(self):
        response = self.post(f"/api/actors/{self.actor.pk}/follow/")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Follow.objects.filter(user=self.alice, actor=self.actor).exists())
        self.assertEqual(len(self.client.get("/api/state/").json()["following"]), 1)

    def test_02_duplicate_follow_returns_400(self):
        Follow.objects.create(user=self.alice, actor=self.actor)
        response = self.post(f"/api/actors/{self.actor.pk}/follow/")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Follow.objects.count(), 1)

    def test_03_unfollow_deletes_only_own_relation(self):
        Follow.objects.create(user=self.alice, actor=self.actor)
        Follow.objects.create(user=self.bob, actor=self.actor)
        self.assertEqual(self.post(f"/api/actors/{self.actor.pk}/unfollow/").status_code, 200)
        self.assertFalse(Follow.objects.filter(user=self.alice, actor=self.actor).exists())
        self.assertTrue(Follow.objects.filter(user=self.bob, actor=self.actor).exists())
        self.assertEqual(self.post(f"/api/actors/{self.actor.pk}/unfollow/").status_code, 404)

    def test_04_release_notifies_distinct_followers(self):
        Follow.objects.create(user=self.alice, actor=self.actor)
        Follow.objects.create(user=self.alice, actor=self.actor2)
        Follow.objects.create(user=self.bob, actor=self.actor2)
        self.client.force_login(self.admin)
        response = self.post("/api/movies/", {"title": "Next", "cast_ids": [self.actor.pk, self.actor2.pk]})
        self.assertEqual(response.status_code, 201)
        self.assertCountEqual(list(Notification.objects.values_list("user_id", flat=True)), [self.alice.pk, self.bob.pk])
        movie = Movie.objects.get(pk=response.json()["id"])
        notify_followers(movie)
        self.assertEqual(Notification.objects.count(), 2)

    def test_05_read_notification_persists_and_updates_count(self):
        movie = Movie.objects.create(title="Next")
        note = Notification.objects.create(user=self.alice, movie=movie)
        self.assertEqual(self.client.get("/api/state/").json()["unread_count"], 1)
        for _ in range(2):
            self.assertEqual(self.post(f"/api/notifications/{note.pk}/read/").status_code, 200)
            note.refresh_from_db()
            self.assertTrue(note.is_read)
            self.assertEqual(self.client.get("/api/state/").json()["unread_count"], 0)

    def test_guard_unknown_actor(self):
        self.assertEqual(self.post("/api/actors/999/follow/").status_code, 404)

    def test_guard_non_admin_cannot_release(self):
        self.assertEqual(self.post("/api/movies/", {"title": "Next", "cast_ids": [self.actor.pk]}).status_code, 403)
        self.assertEqual(Movie.objects.count(), 0)

    def test_guard_cannot_read_someone_elses_notification(self):
        note = Notification.objects.create(user=self.bob, movie=Movie.objects.create(title="Other"))
        self.assertEqual(self.post(f"/api/notifications/{note.pk}/read/").status_code, 404)
        note.refresh_from_db()
        self.assertFalse(note.is_read)

    def test_guard_invalid_cast_does_not_save_movie(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.post("/api/movies/", {"title": "Next", "cast_ids": [self.actor.pk, 999]}).status_code, 404)
        self.assertEqual(Movie.objects.count(), 0)

    def test_guard_login_required(self):
        self.client.logout()
        self.assertEqual(self.client.get("/api/state/").status_code, 401)
