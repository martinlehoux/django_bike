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
    this.socket = new WebSocket(`ws://${location.host}/ws/notification/`);
  }

  deleteNotif(pk: number) {
    this.socket.send(JSON.stringify({ type: "delete", pk }));
  }
}
