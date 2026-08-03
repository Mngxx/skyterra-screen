/* Miniature task board. No framework, no build step, no virtual DOM.
 * This is genuinely how the real SkyTerra SPA is written. */

(function () {
  'use strict';

  var state = {
    areaId: null,
    tag: '',
    tasks: [],
    count: 0
  };

  function el(id) { return document.getElementById(id); }

  function loadAreas() {
    return fetch('/api/areas')
      .then(function (r) { return r.json(); })
      .then(function (body) {
        var select = el('area-select');
        select.innerHTML = '';
        body.areas.filter(function (a) { return !a.archived; })
          .forEach(function (a) {
            var option = document.createElement('option');
            option.value = a.id;
            option.textContent = a.name;
            select.appendChild(option);
          });
        if (!state.areaId && body.areas.length) {
          state.areaId = Number(select.value);
        }
      });
  }

  function loadTasks() {
    if (!state.areaId) { return Promise.resolve(); }
    var url = '/api/tasks?area=' + encodeURIComponent(state.areaId);
    if (state.tag) { url += '&tag=' + encodeURIComponent(state.tag); }
    return fetch(url)
      .then(function (r) { return r.json(); })
      .then(function (body) {
        state.tasks = body.tasks || [];
        state.count = body.count || 0;
        renderTasks();
      });
  }

  function renderTasks() {
    var list = el('task-list');
    // Rebuild the whole list every time. Simple, and it is what the real one
    // does too.
    list.innerHTML = '';

    state.tasks.forEach(function (task) {
      var row = document.createElement('div');
      row.className = 'task';

      var title = document.createElement('span');
      title.className = 'task-title';
      title.textContent = task.title;
      row.appendChild(title);

      var status = document.createElement('select');
      status.className = 'task-status';
      ['open', 'in_progress', 'done'].forEach(function (value) {
        var option = document.createElement('option');
        option.value = value;
        option.textContent = value;
        if (value === task.status) { option.selected = true; }
        status.appendChild(option);
      });
      row.appendChild(status);

      list.appendChild(row);
    });

    el('task-count').textContent = state.count + ' matching';
  }

  function addTask() {
    var input = el('new-title');
    var title = (input.value || '').trim();
    if (!title) { return; }

    fetch('/api/tasks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: title,
        areaId: state.areaId
      })
    })
      .then(function (r) { return r.json(); })
      .then(function () {
        input.value = '';
        loadTasks();
      });
  }

  function wire() {
    el('area-select').addEventListener('change', function (event) {
      state.areaId = Number(event.target.value);
      loadTasks();
    });
    el('tag-filter').addEventListener('input', function (event) {
      state.tag = event.target.value.trim();
      loadTasks();
    });
    el('add-task').addEventListener('click', addTask);
  }

  loadAreas().then(function () {
    wire();
    loadTasks();
    // Poll, so the board stays current while somebody else is working on it.
    setInterval(loadTasks, 1000);
  });
})();
