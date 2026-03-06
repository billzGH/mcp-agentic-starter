"""Tests for examples/task-manager/server.py — TaskManager class."""

import json

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_task_manager(task_manager_mod, tmp_path, monkeypatch):
    """Return a fresh TaskManager instance backed by a temp tasks.json."""
    monkeypatch.setattr(task_manager_mod, "TASKS_FILE", tmp_path / "tasks.json")
    return task_manager_mod.TaskManager()


# ---------------------------------------------------------------------------
# create_task
# ---------------------------------------------------------------------------


def test_create_task_returns_task(task_manager_mod, tmp_path, monkeypatch):
    tm = make_task_manager(task_manager_mod, tmp_path, monkeypatch)
    task = tm.create_task("Buy milk")
    assert task["title"] == "Buy milk"
    assert task["id"] == 1
    assert task["completed"] is False
    assert "created_at" in task


def test_create_task_with_description(task_manager_mod, tmp_path, monkeypatch):
    tm = make_task_manager(task_manager_mod, tmp_path, monkeypatch)
    task = tm.create_task("Buy milk", "Whole milk, 2 gallons")
    assert task["description"] == "Whole milk, 2 gallons"


def test_create_task_increments_id(task_manager_mod, tmp_path, monkeypatch):
    tm = make_task_manager(task_manager_mod, tmp_path, monkeypatch)
    t1 = tm.create_task("First")
    t2 = tm.create_task("Second")
    assert t2["id"] == t1["id"] + 1


# ---------------------------------------------------------------------------
# list_tasks
# ---------------------------------------------------------------------------


def test_list_tasks_empty(task_manager_mod, tmp_path, monkeypatch):
    tm = make_task_manager(task_manager_mod, tmp_path, monkeypatch)
    assert tm.list_tasks() == []


def test_list_tasks_all(task_manager_mod, tmp_path, monkeypatch):
    tm = make_task_manager(task_manager_mod, tmp_path, monkeypatch)
    tm.create_task("Task A")
    tm.create_task("Task B")
    assert len(tm.list_tasks(show_completed=True)) == 2


def test_list_tasks_incomplete_only(task_manager_mod, tmp_path, monkeypatch):
    tm = make_task_manager(task_manager_mod, tmp_path, monkeypatch)
    tm.create_task("Task A")
    tm.create_task("Task B")
    tm.complete_task(1)
    incomplete = tm.list_tasks(show_completed=False)
    assert len(incomplete) == 1
    assert incomplete[0]["title"] == "Task B"


# ---------------------------------------------------------------------------
# complete_task
# ---------------------------------------------------------------------------


def test_complete_task(task_manager_mod, tmp_path, monkeypatch):
    tm = make_task_manager(task_manager_mod, tmp_path, monkeypatch)
    tm.create_task("Do laundry")
    task = tm.complete_task(1)
    assert task["completed"] is True
    assert "completed_at" in task


def test_complete_task_not_found(task_manager_mod, tmp_path, monkeypatch):
    tm = make_task_manager(task_manager_mod, tmp_path, monkeypatch)
    with pytest.raises(ValueError, match="not found"):
        tm.complete_task(999)


# ---------------------------------------------------------------------------
# delete_task
# ---------------------------------------------------------------------------


def test_delete_task(task_manager_mod, tmp_path, monkeypatch):
    tm = make_task_manager(task_manager_mod, tmp_path, monkeypatch)
    tm.create_task("To delete")
    assert tm.delete_task(1) is True
    assert tm.list_tasks() == []


def test_delete_task_not_found(task_manager_mod, tmp_path, monkeypatch):
    tm = make_task_manager(task_manager_mod, tmp_path, monkeypatch)
    assert tm.delete_task(999) is False


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------


def test_tasks_persist_to_disk(task_manager_mod, tmp_path, monkeypatch):
    tasks_file = tmp_path / "tasks.json"
    monkeypatch.setattr(task_manager_mod, "TASKS_FILE", tasks_file)

    tm = task_manager_mod.TaskManager()
    tm.create_task("Persisted task")

    assert tasks_file.exists()
    saved = json.loads(tasks_file.read_text())
    assert len(saved) == 1
    assert saved[0]["title"] == "Persisted task"


def test_tasks_load_from_disk(task_manager_mod, tmp_path, monkeypatch):
    tasks_file = tmp_path / "tasks.json"
    tasks_file.write_text(
        json.dumps([{"id": 1, "title": "Pre-existing", "description": "", "completed": False, "created_at": "2024-01-01T00:00:00"}])
    )
    monkeypatch.setattr(task_manager_mod, "TASKS_FILE", tasks_file)

    tm = task_manager_mod.TaskManager()
    assert len(tm.list_tasks()) == 1
    assert tm.list_tasks()[0]["title"] == "Pre-existing"
