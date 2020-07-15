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

export class HttpService {
  async getNotifications(): Promise<Array<Notif>> {
    return fetch("/notification/")
      .then((res) => res.json())
      .then(dataList => dataList.map(data => new Notif(data)))
  }

  async deleteNotification(pk: number) {
    return fetch(`/notification/${pk}`, {
      method: "DELETE",
    });
  }
}
