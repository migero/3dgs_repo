using System;
using System.IO;
using System.IO.MemoryMappedFiles;
using System.Reflection;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Threading;
using GoPro.Security;

namespace GoPro.Instance
{
	public static class SingleInstance<TApplication> where TApplication : Application
	{
		public delegate void ExceptionOccuredDelegate(Exception exception);

		private static int WM_CREATE_WINDOW;

		private const int HWND_BROADCAST = 65535;

		private const int MAPPED_MEMORY_SIZE = 1024;

		private static MemoryMappedFile m_MappedMemory;

		public static void SetExceptionCallback(ExceptionOccuredDelegate userCallback)
		{
			//IL_0034: Unknown result type (might be due to invalid IL or missing references)
			//IL_003e: Expected O, but got Unknown
			AppDomain.CurrentDomain.UnhandledException += delegate(object s, UnhandledExceptionEventArgs e)
			{
				userCallback(((Exception)e.ExceptionObject).Unwrap());
			};
			((DispatcherObject)Application.get_Current()).get_Dispatcher().add_UnhandledException((DispatcherUnhandledExceptionEventHandler)delegate(object s, DispatcherUnhandledExceptionEventArgs e)
			{
				userCallback(e.get_Exception().Unwrap());
				e.set_Handled(true);
			});
			TaskScheduler.UnobservedTaskException += delegate(object s, UnobservedTaskExceptionEventArgs e)
			{
				((DispatcherObject)Application.get_Current()).get_Dispatcher().Invoke((Action)delegate
				{
					userCallback(e.Exception.Unwrap());
				});
			};
		}

		public static bool Merge(string[] args)
		{
			Assembly entryAssembly = Assembly.GetEntryAssembly();
			string text = Cryptography.ComputeHash(Encoding.UTF8.GetBytes(entryAssembly.GetName().FullName));
			try
			{
				m_MappedMemory = MemoryMappedFile.OpenExisting(text);
			}
			catch (Exception)
			{
			}
			WM_CREATE_WINDOW = NativeMethods.RegisterWindowMessage(text);
			if (m_MappedMemory != null)
			{
				string text2 = string.Join(";", args);
				int num = 0;
				if (text2.Length > 0)
				{
					byte[] bytes = Encoding.GetEncoding("UTF-8").GetBytes(text2);
					num = bytes.Length;
					WriteMappedMemory(bytes);
				}
				NativeMethods.PostMessage((IntPtr)65535, WM_CREATE_WINDOW, IntPtr.Zero, (IntPtr)num);
				Application.get_Current().Shutdown();
				return false;
			}
			try
			{
				m_MappedMemory = MemoryMappedFile.CreateNew(text, 1024L);
			}
			catch (Exception)
			{
			}
			if (m_MappedMemory == null)
			{
				return false;
			}
			Directory.SetCurrentDirectory(Path.GetDirectoryName(new Uri(entryAssembly.Location).LocalPath));
			return true;
		}

		private static byte[] ReadMappedMemory(int bytes)
		{
			MemoryMappedViewAccessor memoryMappedViewAccessor = m_MappedMemory.CreateViewAccessor(0L, 1024L, MemoryMappedFileAccess.Read);
			byte[] array = new byte[bytes];
			memoryMappedViewAccessor.ReadArray(0L, array, 0, bytes);
			memoryMappedViewAccessor.Dispose();
			return array;
		}

		private static void WriteMappedMemory(byte[] buffer)
		{
			MemoryMappedViewAccessor memoryMappedViewAccessor = m_MappedMemory.CreateViewAccessor(0L, 1024L, MemoryMappedFileAccess.Write);
			memoryMappedViewAccessor.WriteArray(0L, buffer, 0, buffer.Length);
			memoryMappedViewAccessor.Flush();
			memoryMappedViewAccessor.Dispose();
		}
	}
}
