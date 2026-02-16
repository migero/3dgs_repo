using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Collections.Specialized;

namespace GoPro.Utils
{
	public class ObservableCollectionSynced<TViewModel, TModel> : ObservableCollection<TViewModel>
	{
		private IList<TModel> mModelList;

		private Func<TViewModel, TModel> mViewModelToModel;

		public ObservableCollectionSynced(IList<TModel> modelList, Func<TModel, TViewModel> modelToViewModel, Func<TViewModel, TModel> viewModelToModel)
		{
			mModelList = modelList;
			mViewModelToModel = viewModelToModel;
			foreach (TModel model in modelList)
			{
				Add(modelToViewModel(model));
			}
			CollectionChanged += ObservableCollectionSynced_CollectionChanged;
		}

		private void ObservableCollectionSynced_CollectionChanged(object sender, NotifyCollectionChangedEventArgs e)
		{
			switch (e.Action)
			{
			case NotifyCollectionChangedAction.Add:
			{
				int count = e.NewItems!.Count;
				for (int i = 0; i < count; i++)
				{
					mModelList.Insert(i + e.NewStartingIndex, mViewModelToModel((TViewModel)e.NewItems![i]));
				}
				break;
			}
			case NotifyCollectionChangedAction.Remove:
			{
				foreach (object item in e.OldItems!)
				{
					mModelList.Remove(mViewModelToModel((TViewModel)item));
				}
				break;
			}
			case NotifyCollectionChangedAction.Replace:
				throw new NotImplementedException();
			case NotifyCollectionChangedAction.Move:
				throw new NotImplementedException();
			case NotifyCollectionChangedAction.Reset:
			{
				mModelList.Clear();
				using IEnumerator<TViewModel> enumerator = GetEnumerator();
				while (enumerator.MoveNext())
				{
					TViewModel current = enumerator.Current;
					mModelList.Add(mViewModelToModel(current));
				}
				break;
			}
			}
		}
	}
}
