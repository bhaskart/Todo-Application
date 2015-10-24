from bottle import default_app, run, route
from bottle import get, put, post, request, template
from bottle import static_file

import sqlite3

if __name__ == "__main__":
    HOME = "./"
else:
    HOME = "/home/bthadise/sites/Bthadise.pythonanywhere.com/"

@route('/')
@route('/todo')
@route('/todo/<status:int>')
def todo_list(status=-1):
	conn = sqlite3.connect(HOME+'todo.db')
	c = conn.cursor()
	if (status >= 0):
		c.execute("SELECT id, task, status FROM todo WHERE status LIKE '"+str(status)+"'")
	else:
		c.execute("SELECT id, task, status FROM todo")
	result = c.fetchall()
	output = template('list_view', rows=result)
	return output

@get('/new') 
def new_item_request():
	return '''
		<p>Enter a new item...</p><br/>
		<form action="/new" method="post">
			To be done: <input name="task" type="text" />
			<input value="Save" type="submit" />
		</form>
	'''
	
@post('/new')
def new_item():
	new = request.forms.get('task', '').strip()

	conn = sqlite3.connect(HOME+'todo.db')
	c = conn.cursor()

	c.execute("INSERT INTO todo (task,status) VALUES (?,?)", (new,1))
	new_id = c.lastrowid

	conn.commit()
	c.close()

	#return '<p>The new task was inserted into the database, the ID is %s</p>' % new_id
	return todo_list()

@route('/edit/<no:int>', method='GET')
def edit_item(no):

	if request.GET.get('save','').strip():
		edit = request.GET.get('task','').strip()
		status = request.GET.get('status','').strip()

		if status == 'open':
			status = 1
		else:
			status = 0

		conn = sqlite3.connect('todo.db')
		c = conn.cursor()
		c.execute("UPDATE todo SET task = ?, status = ? WHERE id LIKE ?", (edit, status, no))
		conn.commit()

		return '<p>The item number %s was successfully updated</p>' % no
	else:
		conn = sqlite3.connect('todo.db')
		c = conn.cursor()
		c.execute("SELECT task FROM todo WHERE id LIKE ?", (str(no)))
		cur_data = c.fetchone()

		return template('edit_task', old=cur_data, no=no)
		
@route('/delete/<no:int>', method='GET')
def confirm_delete_item(no):
	return '''
		<form action="/delete/%s" method="post">
			<input value="Confirm deletion..." type="submit" />
		</form>
	''' % no

@route('/delete/<no:int>', method='POST')
def delete_item(no):
	conn = sqlite3.connect('todo.db')
	c = conn.cursor()
	c.execute("DELETE FROM todo WHERE id LIKE ?", (str(no)))
	conn.commit()
	return '<p>The new task was DELETED from the database, the ID was ' + str(no) + '</p>'
	 		 
@route('/static/<filename>')
def server_static(filename):
	return static_file(filename, root='static')

if __name__ == "__main__":
    run(reloader = True, host="0.0.0.0")
else:
    application = default_app()

