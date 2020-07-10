class Notif {
  public datetime: Date;
  public content: string;
  public level: string;

  constructor({ datetime, content, level }: {datetime: string, content: string, level: string}) {
    this.content = content;
    this.level = level;
    this.datetime = new Date(datetime);
  }
}

class HttpService {
  private baseURL: string;

  async getNotifications() {
    return fetch("/notification/")
      .then((res) => res.json())
      .then(dataList => dataList.map(data => new Notif(data)))
  }
}
