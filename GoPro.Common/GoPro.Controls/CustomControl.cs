using System.ComponentModel;
using System.Runtime.CompilerServices;
using System.Windows.Controls;

namespace GoPro.Controls
{
	public class CustomControl : UserControl, INotifyPropertyChanged
	{
		public event PropertyChangedEventHandler PropertyChanged;

		protected virtual void OnPropertyChanged([CallerMemberName] string propertyName = null)
		{
			this.PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
		}
	}
}
