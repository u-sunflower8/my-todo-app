from __future__ import annotations

import gspread
from google.oauth2.service_account import Credentials
import os
import tkinter as tk
from dataclasses import asdict, dataclass
from datetime import datetime
from tkinter import messagebox, ttk

# --- 設定 ---
# ダウンロードしたJSON鍵ファイルのパス
CREDENTIALS_FILE = "credentials.json"
# 操作したいスプレッドシートの名前
SHEET_NAME = "MyTodoSheet" 

@dataclass(frozen=True)
class TodoItem:
    id: str
    title: str
    content: str
    due_date: str
    done: bool
    created_at: str

def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")

def _new_id() -> str:
    return datetime.now().strftime("%Y%m%d%H%M%S%f")

class TodoApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.items: list[TodoItem] = []
        self.filter_mode = tk.StringVar(value="all")

        self.root.title("Google Sheets ToDo")
        self.root.minsize(700, 500)

        # Google Sheets 認証
        self._authenticate_gspread()

        self._build_ui()
        self._load()
        self._refresh_list()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _authenticate_gspread(self) -> None:
        try:
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
            self.gc = gspread.authorize(creds)
            self.sh = self.gc.open(SHEET_NAME)
            self.worksheet = self.sh.get_worksheet(0)
        except Exception as e:
            messagebox.showerror("認証エラー", f"Google Sheetsへの接続に失敗しました:\n{e}")
            self.root.destroy()

    def _build_ui(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        # 入力エリア
        top = ttk.LabelFrame(self.root, text="新規ToDo追加", padding=10)
        top.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
        
        ttk.Label(top, text="タイトル:").grid(row=0, column=0, sticky="w")
        self.entry_title = ttk.Entry(top)
        self.entry_title.grid(row=0, column=1, sticky="ew", padx=5)

        ttk.Label(top, text="期日 (YYYY-MM-DD):").grid(row=0, column=2, sticky="w")
        self.entry_due = ttk.Entry(top)
        self.entry_due.grid(row=0, column=3, sticky="ew", padx=5)

        ttk.Label(top, text="内容:").grid(row=1, column=0, sticky="nw", pady=5)
        self.entry_content = ttk.Entry(top) # 簡易化のためEntryを使用
        self.entry_content.grid(row=1, column=1, columnspan=3, sticky="ew", padx=5, pady=5)

        add_btn = ttk.Button(top, text="追加", command=self.add_item)
        add_btn.grid(row=2, column=3, sticky="e")
        top.columnconfigure(1, weight=1)
        top.columnconfigure(3, weight=1)

        # リスト表示エリア
        mid = ttk.Frame(self.root, padding=10)
        mid.grid(row=1, column=0, sticky="nsew")
        mid.columnconfigure(0, weight=1)
        mid.rowconfigure(0, weight=1)

        # Listboxの代わりに詳細を表示しやすいよう簡易的なフォーマットで表示
        self.listbox = tk.Listbox(mid, font=("MS Gothic", 10), activestyle="none", selectmode=tk.SINGLE)
        self.listbox.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(mid, orient="vertical", command=self.listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.listbox.configure(yscrollcommand=scrollbar.set)

        # 操作エリア
        bottom = ttk.Frame(self.root, padding=10)
        bottom.grid(row=2, column=0, sticky="ew")
        
        ttk.Radiobutton(bottom, text="すべて", value="all", variable=self.filter_mode, command=self._refresh_list).pack(side="left")
        ttk.Radiobutton(bottom, text="未完了", value="active", variable=self.filter_mode, command=self._refresh_list).pack(side="left", padx=10)
        ttk.Radiobutton(bottom, text="完了", value="done", variable=self.filter_mode, command=self._refresh_list).pack(side="left")

        ttk.Button(bottom, text="削除", command=self.delete_selected).pack(side="right")
        ttk.Button(bottom, text="完了/未完了 切替", command=self.toggle_done_selected).pack(side="right", padx=10)

        self.status = tk.StringVar()
        ttk.Label(self.root, textvariable=self.status, relief="sunken", anchor="w").grid(row=3, column=0, sticky="ew")

    def _format_item(self, item: TodoItem) -> str:
        mark = "✅" if item.done else "⬜"
        return f"{mark} 【{item.title}】 期日: {item.due_date} | 内容: {item.content}"

    def _refresh_list(self) -> None:
        self.listbox.delete(0, tk.END)
        self.view_items = self._filtered_items() # 表示中のアイテムを保持
        for item in self.view_items:
            self.listbox.insert(tk.END, self._format_item(item))
        self._update_status()

    def _filtered_items(self) -> list[TodoItem]:
        mode = self.filter_mode.get()
        if mode == "active":
            return [t for t in self.items if not t.done]
        if mode == "done":
            return [t for t in self.items if t.done]
        return list(self.items)

    def _update_status(self) -> None:
        total = len(self.items)
        done = sum(1 for t in self.items if t.done)
        self.status.set(f" 合計: {total}件 (完了: {done} / 未完了: {total-done})")

    def add_item(self) -> None:
        title = self.entry_title.get().strip()
        due = self.entry_due.get().strip()
        content = self.entry_content.get().strip()

        if not title:
            messagebox.showwarning("入力エラー", "タイトルは必須です。")
            return

        item = TodoItem(
            id=_new_id(),
            title=title,
            content=content,
            due_date=due if due else "なし",
            done=False,
            created_at=_now_iso()
        )
        self.items.append(item)
        self._save()
        self._refresh_list()
        
        # 入力クリア
        self.entry_title.delete(0, tk.END)
        self.entry_due.delete(0, tk.END)
        self.entry_content.delete(0, tk.END)

    def toggle_done_selected(self) -> None:
        selection = self.listbox.curselection()
        if not selection: return
        
        target_id = self.view_items[selection[0]].id
        self.items = [
            TodoItem(t.id, t.title, t.content, t.due_date, not t.done, t.created_at) if t.id == target_id else t
            for t in self.items
        ]
        self._save()
        self._refresh_list()

    def delete_selected(self) -> None:
        selection = self.listbox.curselection()
        if not selection: return
        
        if not messagebox.askyesno("確認", "選択した項目を削除しますか？"): return

        target_id = self.view_items[selection[0]].id
        self.items = [t for t in self.items if t.id != target_id]
        self._save()
        self._refresh_list()

    def _load(self) -> None:
        try:
            records = self.worksheet.get_all_records()
            self.items = [
                TodoItem(
                    id=str(r["id"]),
                    title=str(r["title"]),
                    content=str(r["content"]),
                    due_date=str(r["due_date"]),
                    done=str(r["done"]).lower() == "true",
                    created_at=str(r["created_at"])
                ) for r in records
            ]
        except Exception as e:
            print(f"Load Error: {e}")
            self.items = []

    def _save(self) -> None:
        # ヘッダーの作成
        header = ["id", "title", "content", "due_date", "done", "created_at"]
        data = [header]
        for item in self.items:
            data.append([item.id, item.title, item.content, item.due_date, item.done, item.created_at])
        
        try:
            self.worksheet.clear()
            self.worksheet.update('A1', data)
        except Exception as e:
            messagebox.showerror("保存エラー", f"スプレッドシートへの保存に失敗しました:\n{e}")

    def _on_close(self) -> None:
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()