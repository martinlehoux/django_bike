export class Notif {
  public datetime: Date;
  public content: string;
  public level: string;
  public pk: number;

  constructor(
    { datetime, content, level, pk }:
    {datetime: string, content: string, level: string, pk: number}
  ) {
    this.pk = pk;
    this.content = content;
    this.level = level;
    this.datetime = new Date(datetime);
  }
}


export class WebSocketMessage {
  public type: "list" | "new" | "delete"
  public notification: any
  public notifications: Array<any>
  public pk: number
}

export class WebSocketService {
  public socket: WebSocket

  constructor() {
    const wsProto = window.location.protocol === "https:" ? "wss:" : "ws:";
    const url = `${wsProto}//${location.host}/ws/notification/`;
    console.log("Attempting websocket connection to:", url);
    this.socket = new WebSocket(url);
  }

  deleteNotif(pk: number) {
    this.socket.send(JSON.stringify({ type: "delete", pk }));
  }
}
