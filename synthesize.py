#!/usr/bin/env python3
import argparse
import grpc
import time

from flask import Flask, render_template, request
from synthesis_pb2 import AsyncSynthesisRequest
from synthesis_pb2_grpc import SmartSpeechStub
from storage_pb2 import UploadRequest, DownloadRequest
from storage_pb2_grpc import SmartSpeechStub as StorageSmartSpeechStub
from task_pb2 import GetTaskRequest
from task_pb2_grpc import SmartSpeechStub as TaskSmartSpeechStub

SLEEP_TIME = 5
CHUNK_SIZE = 4096

app = Flask(__name__)

def generate_chunks(path, chunk_size=CHUNK_SIZE):
    with open(path, 'rb') as f:
        for data in iter(lambda: f.read(chunk_size), b''):
            yield UploadRequest(file_chunk=data)


def synthesize_async(args):
    ssl_cred = grpc.ssl_channel_credentials(
        root_certificates=open(args.ca, 'rb').read() if args.ca else None
    )
    token_cred = grpc.access_token_call_credentials(args.token)

    channel = grpc.secure_channel(
        args.host,
        grpc.composite_channel_credentials(ssl_cred, token_cred)
    )

    synthesis_stub = SmartSpeechStub(channel)
    storage_stub = StorageSmartSpeechStub(channel)
    task_stub = TaskSmartSpeechStub(channel)

    try:
        upload_response = storage_stub.Upload(generate_chunks(args.text))
        print('Input file has been uploaded:', upload_response.request_file_id)

        synthesis_task = synthesis_stub.AsyncSynthesize(
            AsyncSynthesisRequest(
                request_file_id=upload_response.request_file_id,
                audio_encoding=args.audio_encoding,
                voice=args.voice,
            )
        )
        print('Task has been created:', synthesis_task.id)

        while True:
            time.sleep(SLEEP_TIME)

            task = task_stub.GetTask(GetTaskRequest(task_id=synthesis_task.id))
            if task.status == task_pb2.Task.NEW:
                print('-', end='', flush=True)
                continue
            elif task.status == task_pb2.Task.RUNNING:
                print('+', end='', flush=True)
                continue
            elif task.status == task_pb2.Task.CANCELED:
                print('\nTask has been canceled')
                break
            elif task.status == task_pb2.Task.ERROR:
                print('\nTask has failed:', task.error)
                break
            elif task.status == task_pb2.Task.DONE:
                print('\nTask has finished successfully:', task.response_file_id)
                download_response = storage_stub.Download(DownloadRequest(response_file_id=task.response_file_id))
                with open(args.file, 'wb') as f:
                    for chunk in download_response:
                        f.write(chunk.file_chunk)
                print('Output file has been downloaded')
                break
    except grpc.RpcError as err:
        print('RPC error: code = {}, details = {}'.format(err.code(), err.details()))
    except Exception as exc:
        print('Exception:', exc)
    finally:
        channel.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/synthesize', methods=['POST'])
def synthesize():
    host = request.form.get('host')
    token = request.form.get('token')
    text = request.form.get('text')
    audio_encoding = request.form.get('audio_encoding')
    voice = request.form.get('voice')
    file = request.form.get('file')

    args = argparse.Namespace(
        host=host,
        token=token,
        text=text,
        audio_encoding=audio_encoding,
        voice=voice,
        file=file
    )

    synthesize_async(args)

    return render_template('success.html', file=file)

def main():
    app.run()

if __name__ == '__main__':
    main()
