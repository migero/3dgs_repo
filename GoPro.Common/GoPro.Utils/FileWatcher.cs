using System;
using System.Collections.Generic;
using System.IO;
using System.Management;
using System.Windows.Threading;

namespace GoPro.Utils
{
	public class FileWatcher
	{
		public delegate void FileMovedDelegate(string oldFilepath, string newFilepath);

		public delegate void FileDeletedDelegate(string filepath);

		public delegate void FileOfflineDelegate(string filepath);

		public delegate void FileOnlineDelegate(string filepath);

		internal class DirectoryWatcher
		{
			public FileSystemWatcher Watcher;

			public List<string> FileNames;
		}

		private Dictionary<string, DirectoryWatcher> m_Directories;

		private Dispatcher mDispatcher;

		private ManagementEventWatcher mWMIInstanceCreationEventWatcher;

		private ManagementEventWatcher mWMIInstanceDeletionEventWatcher;

		public event FileMovedDelegate FileMoved;

		public event FileDeletedDelegate FileDeleted;

		public event FileOfflineDelegate FileOffline;

		public event FileOnlineDelegate FileOnline;

		public FileWatcher(Dispatcher dispatcher)
		{
			mDispatcher = dispatcher;
			m_Directories = new Dictionary<string, DirectoryWatcher>();
			CreateWMIEventWatchers();
			StartWMIEventWatchers();
		}

		~FileWatcher()
		{
			StopWMIEventWatchers();
			ClearWMIEventWatchers();
		}

		private void CreateWMIEventWatchers()
		{
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_0010: Expected O, but got Unknown
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0015: Expected O, but got Unknown
			//IL_0022: Unknown result type (might be due to invalid IL or missing references)
			//IL_002c: Expected O, but got Unknown
			//IL_0032: Unknown result type (might be due to invalid IL or missing references)
			//IL_003c: Expected O, but got Unknown
			//IL_0037: Unknown result type (might be due to invalid IL or missing references)
			//IL_0041: Expected O, but got Unknown
			//IL_004e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0058: Expected O, but got Unknown
			mWMIInstanceCreationEventWatcher = new ManagementEventWatcher((EventQuery)new WqlEventQuery("SELECT * FROM __InstanceCreationEvent WITHIN 1 WHERE TargetInstance ISA 'Win32_LogicalDisk'\r\n                            AND (TargetInstance.DriveType = 2 OR TargetInstance.DriveType = 3 OR TargetInstance.DriveType = 4)"));
			mWMIInstanceCreationEventWatcher.add_EventArrived(new EventArrivedEventHandler(OnWMIInstanceOperationEvent));
			mWMIInstanceDeletionEventWatcher = new ManagementEventWatcher((EventQuery)new WqlEventQuery("SELECT * FROM __InstanceDeletionEvent WITHIN 1 WHERE TargetInstance ISA 'Win32_LogicalDisk'\r\n                            AND (TargetInstance.DriveType = 2 OR TargetInstance.DriveType = 3 OR TargetInstance.DriveType = 4)"));
			mWMIInstanceDeletionEventWatcher.add_EventArrived(new EventArrivedEventHandler(OnWMIInstanceOperationEvent));
		}

		private void ClearWMIEventWatchers()
		{
			mWMIInstanceCreationEventWatcher = null;
			mWMIInstanceDeletionEventWatcher = null;
		}

		private void StartWMIEventWatchers()
		{
			if (mWMIInstanceCreationEventWatcher != null)
			{
				mWMIInstanceCreationEventWatcher.Start();
			}
			if (mWMIInstanceDeletionEventWatcher != null)
			{
				mWMIInstanceDeletionEventWatcher.Start();
			}
		}

		private void StopWMIEventWatchers()
		{
			if (mWMIInstanceCreationEventWatcher != null)
			{
				mWMIInstanceCreationEventWatcher.Stop();
			}
			if (mWMIInstanceDeletionEventWatcher != null)
			{
				mWMIInstanceDeletionEventWatcher.Stop();
			}
		}

		public void AddFile(string filepath)
		{
			if (filepath != null)
			{
				DirectoryWatcher directoryWatcher = GetDirectoryWatcher(filepath, create: true);
				string fileName = Path.GetFileName(filepath);
				directoryWatcher.FileNames.Add(fileName);
			}
		}

		public void RemoveFile(string filepath)
		{
			if (filepath == null)
			{
				return;
			}
			DirectoryWatcher directoryWatcher = GetDirectoryWatcher(filepath, create: false);
			if (directoryWatcher != null)
			{
				string fileName = Path.GetFileName(filepath);
				directoryWatcher.FileNames.Remove(fileName);
				if (directoryWatcher.FileNames.Count == 0)
				{
					directoryWatcher.Watcher.EnableRaisingEvents = false;
					string directoryName = Path.GetDirectoryName(filepath);
					m_Directories.Remove(directoryName);
				}
			}
		}

		private void OnFileRenamedInternal(object sender, FileSystemEventArgs e)
		{
			mDispatcher.Invoke((Action)delegate
			{
				RenamedEventArgs renamedEventArgs = (RenamedEventArgs)e;
				DirectoryWatcher directoryWatcher = GetDirectoryWatcher(renamedEventArgs.OldFullPath, create: false);
				if (IsWatchedFile(renamedEventArgs.OldFullPath, directoryWatcher))
				{
					string fileName = Path.GetFileName(renamedEventArgs.OldFullPath);
					string fileName2 = Path.GetFileName(renamedEventArgs.FullPath);
					directoryWatcher.FileNames.Remove(fileName);
					directoryWatcher.FileNames.Add(fileName2);
					if (this.FileMoved != null)
					{
						this.FileMoved(renamedEventArgs.OldFullPath, renamedEventArgs.FullPath);
					}
				}
			});
		}

		private void OnFileMovedOrDeletedInternal(object sender, FileSystemEventArgs e)
		{
			mDispatcher.Invoke((Action)delegate
			{
				if (IsWatchedFile(e.FullPath))
				{
					if (this.FileDeleted != null)
					{
						this.FileDeleted(e.FullPath);
					}
					RemoveFile(e.FullPath);
				}
			});
		}

		private void OnWMIInstanceOperationEvent(object sender, EventArrivedEventArgs e)
		{
			try
			{
				PropertyData val = e.get_NewEvent().get_Properties().get_Item("TargetInstance");
				if (val != null)
				{
					object value = val.get_Value();
					PropertyData val2 = ((ManagementBaseObject)((value is ManagementBaseObject) ? value : null)).get_Properties().get_Item("DeviceID");
					if (e.get_NewEvent().get_ClassPath().get_ClassName() == "__InstanceDeletionEvent")
					{
						VolumeRemoved(val2.get_Value().ToString());
					}
					else if (e.get_NewEvent().get_ClassPath().get_ClassName() == "__InstanceCreationEvent")
					{
						VolumeConnected(val2.get_Value().ToString());
					}
				}
			}
			catch
			{
			}
		}

		private bool IsWatchedFile(string filepath)
		{
			DirectoryWatcher directoryWatcher = GetDirectoryWatcher(filepath, create: false);
			return IsWatchedFile(filepath, directoryWatcher);
		}

		private bool IsWatchedFile(string filepath, DirectoryWatcher directory)
		{
			if (directory != null)
			{
				string fileName = Path.GetFileName(filepath);
				return directory.FileNames.Contains(fileName);
			}
			return false;
		}

		private void VolumeRemoved(string root)
		{
			foreach (string path in m_Directories.Keys)
			{
				if (!Path.GetPathRoot(path)!.Contains(root) || !m_Directories.TryGetValue(path, out var watcher))
				{
					continue;
				}
				mDispatcher.Invoke((Action)delegate
				{
					watcher.Watcher.EnableRaisingEvents = false;
					List<string> list = new List<string>();
					foreach (string fileName in watcher.FileNames)
					{
						string item = Path.Combine(path, fileName);
						list.Add(item);
					}
					foreach (string item2 in list)
					{
						if (this.FileOffline != null)
						{
							this.FileOffline(item2);
						}
					}
				});
			}
		}

		private void VolumeConnected(string root)
		{
			foreach (string path in m_Directories.Keys)
			{
				if (!Path.GetPathRoot(path)!.Contains(root) || !m_Directories.TryGetValue(path, out var watcher))
				{
					continue;
				}
				mDispatcher.Invoke((Action)delegate
				{
					watcher.Watcher.EnableRaisingEvents = true;
					List<string> list = new List<string>();
					foreach (string fileName in watcher.FileNames)
					{
						string item = Path.Combine(path, fileName);
						list.Add(item);
					}
					foreach (string item2 in list)
					{
						if (!File.Exists(item2))
						{
							RemoveFile(item2);
						}
						else if (this.FileOnline != null)
						{
							this.FileOnline(item2);
						}
					}
				});
			}
		}

		private DirectoryWatcher GetDirectoryWatcher(string filepath, bool create)
		{
			string directoryName = Path.GetDirectoryName(filepath);
			DirectoryWatcher value = null;
			if (!m_Directories.TryGetValue(directoryName, out value) && create)
			{
				value = new DirectoryWatcher();
				value.Watcher = new FileSystemWatcher();
				value.Watcher.Renamed += OnFileRenamedInternal;
				value.Watcher.Deleted += OnFileMovedOrDeletedInternal;
				value.Watcher.Path = directoryName;
				value.Watcher.EnableRaisingEvents = true;
				value.FileNames = new List<string>();
				m_Directories.Add(directoryName, value);
			}
			return value;
		}
	}
}
