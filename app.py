from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'dev-secret-key-change-me'  # нужен для flash-сообщений

# Хранилище задач
tasks = []
next_id = 1

# Ограничения для валидации
MAX_TITLE_LENGTH = 100


def validate_title(title):
    """Ручная валидация названия задачи.
    Возвращает (ok: bool, error: str | None)."""
    if not title:
        return False, "Название задачи не может быть пустым."
    if len(title) > MAX_TITLE_LENGTH:
        return False, f"Название не должно превышать {MAX_TITLE_LENGTH} символов."
    return True, None


@app.route('/')
def index():
    return render_template('index.html', tasks=tasks)


@app.route('/add', methods=['POST'])
def add_task():
    global next_id
    title = request.form.get('title', '').strip()

    ok, error = validate_title(title)
    if not ok:
        flash(error, 'error')
        return redirect(url_for('index'))

    tasks.append({
        'id': next_id,
        'title': title,
        'done': False
    })
    next_id += 1
    flash('Задача добавлена.', 'success')
    return redirect(url_for('index'))


@app.route('/toggle/<int:task_id>')
def toggle_task(task_id):
    task = next((t for t in tasks if t['id'] == task_id), None)
    if task is None:
        flash('Задача не найдена.', 'error')
    else:
        task['done'] = not task['done']
    return redirect(url_for('index'))


@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = next((t for t in tasks if t['id'] == task_id), None)
    if task is None:
        flash('Задача не найдена.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        new_title = request.form.get('title', '').strip()
        ok, error = validate_title(new_title)
        if not ok:
            flash(error, 'error')
            # остаёмся на странице редактирования, передаём введённое значение
            return render_template('edit.html', task=task, draft=new_title), 400

        task['title'] = new_title
        flash('Задача обновлена.', 'success')
        return redirect(url_for('index'))

    return render_template('edit.html', task=task, draft=task['title'])


@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    global tasks
    before = len(tasks)
    tasks = [t for t in tasks if t['id'] != task_id]
    if len(tasks) == before:
        flash('Задача не найдена.', 'error')
    else:
        flash('Задача удалена.', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)