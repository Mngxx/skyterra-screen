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

  var rowsById = {};   // task.id -> its <div class="task"> node, kept across polls
  var RENDER_STEP = 200;          // how many more rows "Load more" reveals per click
  var renderLimit = RENDER_STEP;  // how many rows to render right now; grows via Load more

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

  function createTaskRow() {
    var row = document.createElement('div');
    row.className = 'task';

    var title = document.createElement('span');
    title.className = 'task-title';
    row.appendChild(title);

    var status = document.createElement('select');
    status.className = 'task-status';
    ['open', 'in_progress', 'done'].forEach(function (value) {
      var option = document.createElement('option');
      option.value = value;
      option.textContent = value;
      status.appendChild(option);
    });
    row.appendChild(status);

    row._title = title;
    row._status = status;
    return row;
  }

  function updateTaskRow(row, task) {
    if (row._title.textContent !== task.title) {
      row._title.textContent = task.title;
    }
    // Don't touch the select while the user has it focused/open, or a poll
    // mid-choice would overwrite what they're picking.
    if (document.activeElement !== row._status && row._status.value !== task.status) {
      row._status.value = task.status;
    }
  }

  function renderTasks() {
    var list = el('task-list');
    var seenIds = {};
    // Render only up to renderLimit rows at a time so a large, unfiltered
    // area doesn't put tens of thousands of nodes in the DOM at once. The
    // rest is still fetched and still reachable via "Load more" below -
    // nothing is ever hidden from the user, just not all rendered together.
    var visible = state.tasks.slice(0, renderLimit);

    visible.forEach(function (task) {
      seenIds[task.id] = true;
      var row = rowsById[task.id];
      if (!row) {
        row = createTaskRow();
        rowsById[task.id] = row;
      }
      updateTaskRow(row, task);
      // appendChild on a node already in the DOM moves it rather than
      // duplicating it, so this reorders existing rows without recreating
      // them - recreating is what was closing an open dropdown every poll.
      list.appendChild(row);
    });

    // Also drops rows that fell outside the cap on this poll, same cleanup
    // path as rows for tasks that were filtered or deleted.
    Object.keys(rowsById).forEach(function (id) {
      if (!seenIds[id]) {
        rowsById[id].remove();
        delete rowsById[id];
      }
    });

    var countText = state.count + ' matching';
    if (state.tasks.length > renderLimit) {
      countText += ' (showing ' + renderLimit + ')';
    }
    el('task-count').textContent = countText;

    var loadMore = el('load-more');
    var remaining = state.tasks.length - renderLimit;
    if (remaining > 0) {
      loadMore.textContent = 'Load ' + Math.min(RENDER_STEP, remaining) + ' more (' + remaining + ' remaining)';
      loadMore.style.display = '';
    } else {
      loadMore.style.display = 'none';
    }
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
      renderLimit = RENDER_STEP;   // new context, start from the top again
      loadTasks();
    });
    el('tag-filter').addEventListener('input', function (event) {
      state.tag = event.target.value.trim();
      renderLimit = RENDER_STEP;   // new context, start from the top again
      loadTasks();
    });
    el('add-task').addEventListener('click', addTask);
    el('load-more').addEventListener('click', function () {
      // Tasks are already fetched in full (the API isn't paginated), so
      // revealing more is just a re-render with a higher limit, no request.
      renderLimit += RENDER_STEP;
      renderTasks();
    });
  }

  loadAreas().then(function () {
    wire();
    loadTasks();
    // Poll, so the board stays current while somebody else is working on it.
    setInterval(loadTasks, 1000);
  });
})();
