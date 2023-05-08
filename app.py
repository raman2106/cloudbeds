from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def home():
  #Log the client's IP'
  client_ip = request.remote_addr
  print(f'Client IP:{client_ip}')#Improvement: Should we log it to a log file?
  return render_template("home.html")


if __name__ == "__main__":
  app.run(host="0.0.0.0", debug=True)
